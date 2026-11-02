"""Build and inspect reproducible platform packages from a committed revision and engine."""

import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_FORMAT = 2
VERSIONS = (
    ("HEAD", "Current integration; both engines, default legacy"),
    (
        "coding-agent-candidate-2026-11-02",
        "Sealed coding candidate; not a platform score",
    ),
    ("teacher-contracts-2026-11-01", "Legacy with teacher contracts"),
    ("optimized-verified-2026-11-01", "Earlier verified legacy checkpoint"),
)


def git(*args, root=ROOT):
    return subprocess.check_output(["git", *args], cwd=root)


def resolve_revision(ref, root=ROOT):
    return (
        git("rev-parse", "--verify", "--end-of-options", ref + "^{commit}", root=root)
        .decode()
        .strip()
    )


def runtime_files(revision, engine, root=ROOT):
    selected = []
    for record in git("ls-tree", "-rz", "--full-tree", revision, root=root).split(
        b"\0"
    ):
        if not record:
            continue
        metadata, name = record.split(b"\t", 1)
        mode, kind, identity = metadata.decode().split()
        name = name.decode()
        include = name in {"main.py", "requirements.txt"} or name.startswith(
            "infrastructure/"
        )
        if engine == "coding":
            include |= name.startswith("coding_agent/")
        else:
            include |= (
                name == "run_all.py"
                or name.startswith("legacy/")
                or bool(re.fullmatch(r"\d\d_[^/]+\.py", name))
            )
        if not include:
            continue
        if kind != "blob" or mode not in {"100644", "100755"}:
            raise ValueError("Unsupported runtime source: " + name)
        selected.append((name, identity, mode))
    required = {"main.py", "requirements.txt", "infrastructure/utils/cli.py"}
    if engine == "coding":
        required.add("coding_agent/loop.py")
    else:
        required.add("run_all.py")
        for number in range(13):
            if not any(
                re.fullmatch(rf"(?:legacy/)?{number:02d}_[^/]+\.py", row[0])
                for row in selected
            ):
                raise ValueError(f"Revision lacks legacy stage {number:02d}")
    names = {r[0] for r in selected}
    if not required <= names:
        raise ValueError(
            f"Revision does not support {engine}: missing {sorted(required - names)}"
        )
    raw = subprocess.check_output(
        ["git", "cat-file", "--batch"],
        cwd=root,
        input="".join(row[1] + "\n" for row in selected).encode(),
    )
    stream, files, modes = io.BytesIO(raw), {}, {}
    for name, identity, mode in selected:
        header = stream.readline().decode().split()
        if header[:2] != [identity, "blob"]:
            raise ValueError("Invalid source object: " + name)
        files[name] = stream.read(int(header[2]))
        if stream.read(1) != b"\n":
            raise ValueError("Truncated source object")
        modes[name] = int(mode, 8)
    return files, modes


def default_output(ref, engine, root=ROOT):
    revision = resolve_revision(ref, root)
    return root / "dist" / f"agent-{engine}-{revision[:12]}-v{PACKAGE_FORMAT}.zip"


def inspect_package(output):
    output = Path(output).resolve()
    manifest = json.loads(output.with_suffix(".json").read_text())
    if manifest.get("package_format") != PACKAGE_FORMAT:
        raise ValueError(
            "Unsupported package manifest format; rebuild with the current packager"
        )
    content = output.read_bytes()
    if hashlib.sha256(content).hexdigest() != manifest["zip_sha256"]:
        raise ValueError("ZIP hash differs from manifest")
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Duplicate archive paths")
        if not {"main.py", "_agent_main.py", "requirements.txt"} <= set(names):
            raise ValueError("Required submission entrypoints are missing")
        files = {}
        for name in names:
            if name.startswith("/") or "\\" in name or ".." in name.split("/"):
                raise ValueError("Unsafe archive path: " + name)
            data = archive.read(name)
            files[name] = hashlib.sha256(data).hexdigest()
            if name.endswith(".py"):
                compile(data, name, "exec")
        if files != manifest["files"]:
            raise ValueError("Archive files differ from manifest")
        for name, digest in manifest["source_files"].items():
            packaged_name = "_agent_main.py" if name == "main.py" else name
            if files.get(packaged_name) != digest:
                raise ValueError("Original committed source differs: " + name)
    return manifest


def package(output=None, ref="HEAD", engine="legacy", *, root=ROOT):
    if engine not in {"legacy", "coding"}:
        raise ValueError("Engine must be legacy or coding")
    revision = resolve_revision(ref, root)
    output = Path(output or default_output(revision, engine, root)).resolve()
    if output.suffix != ".zip":
        raise ValueError("Output must be a .zip file")
    files, modes = runtime_files(revision, engine, root)
    source_hashes = {
        name: hashlib.sha256(data).hexdigest() for name, data in files.items()
    }
    # The platform injects URL/key, whereas historical legacy clients also require MODEL.
    files["_agent_main.py"] = files.pop("main.py")
    modes["_agent_main.py"] = modes.pop("main.py")
    files["main.py"] = (
        '"""Platform adapter for the selected committed engine."""\n'
        "import os\nimport runpy\nfrom pathlib import Path\n"
        'os.environ["MODEL"] = os.environ.get("MODEL") or "deepseek-flash"\n'
        f'os.environ["ARC_AGENT_ENGINE"] = {engine!r}\n'
        'runpy.run_path(str(Path(__file__).with_name("_agent_main.py")), run_name="__main__")\n'
    ).encode()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, (2020, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = modes.get(name, 0o100644) << 16
            archive.writestr(info, data)
    content = buffer.getvalue()
    manifest = {
        "package_format": PACKAGE_FORMAT,
        "revision": revision,
        "requested_ref": ref,
        "default_engine": engine,
        "zip_path": str(output),
        "zip_sha256": hashlib.sha256(content).hexdigest(),
        "files": {
            name: hashlib.sha256(data).hexdigest() for name, data in files.items()
        },
        "source_files": source_hashes,
        "entrypoint_adapter": "Original main.py preserved as _agent_main.py; default MODEL and fixed engine supplied by wrapper. No credentials or endpoint overrides.",
    }
    if output.exists():
        previous = inspect_package(output)
        if output.read_bytes() != content:
            raise ValueError(
                "Refusing to overwrite a different package: " + str(output)
            )
        for key in ("revision", "default_engine", "files", "source_files"):
            if previous[key] != manifest[key]:
                raise ValueError("Existing package manifest differs: " + key)
        return previous
    if output.with_suffix(".json").exists():
        raise ValueError("Refusing to overwrite an existing manifest")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream:
        stream.write(content)
    output.with_suffix(".json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    )
    return manifest


def list_versions():
    for ref, description in VERSIONS:
        revision = resolve_revision(ref)
        paths = git("ls-tree", "-r", "--name-only", revision).decode().splitlines()
        engines = [
            name
            for name, path in (
                ("legacy", "run_all.py"),
                ("coding", "coding_agent/loop.py"),
            )
            if path in paths
        ]
        print(f"{ref:40} {revision[:12]}  {','.join(engines):14} {description}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, nargs="?")
    parser.add_argument("--ref", default="HEAD")
    parser.add_argument("--engine", choices=("legacy", "coding"), default="legacy")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--list", action="store_true")
    actions.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if args.list:
            list_versions()
        else:
            output = args.output or default_output(args.ref, args.engine)
            result = (
                inspect_package(output)
                if args.check
                else package(output, args.ref, args.engine)
            )
            print(
                json.dumps(
                    {
                        key: result[key]
                        for key in (
                            "revision",
                            "default_engine",
                            "zip_path",
                            "zip_sha256",
                        )
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        parser.exit(1, str(error) + "\n")
