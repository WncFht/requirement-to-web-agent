"""Build and verify a small source-history handoff and optional raw evidence pack."""

import argparse
from datetime import date
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import tarfile
import tempfile

FORBIDDEN = {"secret", ".env", ".venv", "node_modules", "work", ".git"}
PREFIX = "lab6-handoff"


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def verify(path):
    with tarfile.open(path, "r:gz") as bundle:
        members = bundle.getmembers()
        names = [m.name for m in members]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate archive member")
        for member in members:
            parts = PurePosixPath(member.name).parts
            if (
                not member.isfile()
                or not parts
                or parts[0] != PREFIX
                or chr(92) in member.name
                or ".." in parts
                or set(parts) & FORBIDDEN
            ):
                raise ValueError(f"Forbidden or unsafe member: {member.name}")
        manifests = [
            name
            for name in names
            if name
            in {PREFIX + "/CORE-MANIFEST.json", PREFIX + "/EVIDENCE-MANIFEST.json"}
        ]
        if len(manifests) != 1:
            raise ValueError("Expected exactly one package manifest")
        with bundle.extractfile(manifests[0]) as stream:
            manifest = json.load(stream)
        expected = {PREFIX + "/" + name for name in manifest["files"]}
        if set(names) != expected | {manifests[0]}:
            raise ValueError("Archive inventory differs from manifest")
        for name, expected_hash in manifest["files"].items():
            with bundle.extractfile(PREFIX + "/" + name) as stream:
                actual = hashlib.file_digest(stream, "sha256").hexdigest()
            if actual != expected_hash:
                raise ValueError(f"Archive content mismatch: {name}")
    return manifest


def write_package(lab, paths, target, revision, kind):
    files = {}
    for relative in sorted(set(paths)):
        path = lab / relative
        if (
            path.is_symlink()
            or not path.is_file()
            or not path.resolve().is_relative_to(lab)
        ):
            raise ValueError(f"Missing or unsafe package input: {relative}")
        if set(PurePosixPath(relative).parts) & FORBIDDEN:
            raise ValueError(f"Private or runtime input: {relative}")
        files[relative] = digest(path)
    manifest = {
        "kind": kind,
        "source_revision": revision,
        "files": files,
        "full_generation_status": "FAILED; new admission guard needs a fresh full run",
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="lab6-package-") as folder:
        staged = Path(folder) / target.name
        with tarfile.open(staged, "w:gz") as bundle:
            for relative in files:
                bundle.add(
                    lab / relative, arcname=PREFIX + "/" + relative, recursive=False
                )
            raw = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
            entry = tarfile.TarInfo(PREFIX + "/" + kind.upper() + "-MANIFEST.json")
            entry.size = len(raw)
            bundle.addfile(entry, io.BytesIO(raw))
        verify(staged)
        target.write_bytes(staged.read_bytes())
    return {
        "file": target.name,
        "bytes": target.stat().st_size,
        "sha256": digest(target),
        "verified_files": len(files),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--lab-dir", type=Path, default=Path(__file__).resolve().parents[2]
    )
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.verify:
        print(json.dumps(verify(args.verify), ensure_ascii=False, indent=2))
        return
    label = date.fromisoformat(args.date).isoformat()
    lab = args.lab_dir.resolve()
    source = lab / "source"
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=source, text=True
    ).strip()
    export = json.loads((lab / "artifacts/compiler-export.json").read_text())
    if (
        revision != export["source_revision"]
        or digest(lab / export["bundle"]) != export["bundle_sha256"]
    ):
        raise ValueError("Export the current committed source before packaging")
    rendered = json.loads((lab / "report/generated/run-summary.json").read_text())
    if not revision.startswith(rendered["source_revision"]):
        raise ValueError("Rebuild report/slide materials for the exported source")
    core = [
        "README.md",
        "source.json",
        "upstream.patch",
        export["bundle"],
        "artifacts/compiler-export.json",
        "report/main.tex",
        "report/main.pdf",
        "slides/main.tex",
        "slides/main.pdf",
    ]
    for folder in [lab / "tools", lab / "report/assets", lab / "report/generated"]:
        core += [p.relative_to(lab).as_posix() for p in folder.iterdir() if p.is_file()]
    evidence = ["artifacts/optimization-runs.json"]
    for folder in [
        lab / "artifacts/teammate-baseline",
        lab / "artifacts/optimization-runs",
    ]:
        evidence += [
            p.relative_to(lab).as_posix() for p in folder.rglob("*") if p.is_file()
        ]
    dist = lab / "dist"
    results = [
        write_package(
            lab, core, dist / f"lab6-handoff-{label}.tar.gz", revision, "core"
        ),
        write_package(
            lab, evidence, dist / f"lab6-evidence-{label}.tar.gz", revision, "evidence"
        ),
    ]
    (lab / "artifacts/handoff-build.json").write_text(
        json.dumps(
            {"date": label, "source_revision": revision, "packages": results}, indent=2
        )
        + "\n"
    )
    for item in results:
        (dist / (item["file"] + ".sha256")).write_text(
            item["sha256"] + "  " + item["file"] + "\n"
        )
    (dist / "SHA256SUMS").write_text(
        "".join(item["sha256"] + "  " + item["file"] + "\n" for item in results)
    )
    (dist / "README.md").write_text(
        "# 分享文件\n\n默认发送 handoff 包与 SHA256SUMS；需要复核原始运行时追加 evidence 包。两个包均解压到 lab6-handoff/，证据包追加到同一目录。先解压 handoff，再按根 README 恢复源码。包中没有模型凭据或依赖。\n"
    )
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
