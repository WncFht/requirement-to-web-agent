"""Archive run evidence, verify every member, then optionally prune dependencies."""

import argparse
import hashlib
import io
import json
from pathlib import Path
import shutil
import tarfile

TREES = (
    ".arc",
    "backend/src",
    "backend/tests",
    "backend/scripts",
    "frontend/src",
    "frontend/tests",
    "frontend/scripts",
    "frontend/public",
)
CONFIG_SUFFIXES = {".json", ".ts", ".js", ".mjs", ".html", ".css", ".sh"}


def archive(run, destination, prune=False):
    run = run.resolve()
    if not (run / ".arc").is_dir():
        raise ValueError(f"Not a compiler run: {run}")
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / (run.name + ".tar.gz")
    if target.exists():
        raise ValueError(f"Refusing to overwrite evidence: {target}")
    selected = set()
    for name in TREES:
        selected.update(p for p in (run / name).rglob("*") if p.is_file())
    for folder in (run, run / "frontend", run / "backend"):
        if not folder.is_dir():
            continue
        selected.update(
            p for p in folder.iterdir() if p.is_file() and p.suffix in CONFIG_SUFFIXES
        )
    selected.update(
        run / name
        for name in ("compiler.log", "model_calls.jsonl", "model_calls.jsonl.gz")
        if (run / name).is_file()
    )
    files = {}
    for path in sorted(selected):
        if path.is_symlink() or not path.resolve().is_relative_to(run):
            raise ValueError(f"Refusing symlink or escaped evidence: {path}")
        relative = path.relative_to(run).as_posix()
        with path.open("rb") as stream:
            files[relative] = {
                "sha256": hashlib.file_digest(stream, "sha256").hexdigest(),
                "bytes": path.stat().st_size,
            }
    manifest = {
        "run": run.name,
        "files": files,
        "scope": "Source, frozen tests, IR, configs and audit logs; no credentials, dependencies or databases",
    }
    temporary = target.with_suffix(target.suffix + ".tmp")
    try:
        with tarfile.open(temporary, "w:gz") as bundle:
            for path in sorted(selected):
                bundle.add(
                    path,
                    arcname=run.name + "/" + path.relative_to(run).as_posix(),
                    recursive=False,
                )
            raw = (json.dumps(manifest, indent=2) + "\n").encode()
            entry = tarfile.TarInfo(run.name + "/archive-manifest.json")
            entry.size = len(raw)
            bundle.addfile(entry, io.BytesIO(raw))
        with tarfile.open(temporary, "r:gz") as bundle:
            for relative, item in files.items():
                with bundle.extractfile(run.name + "/" + relative) as stream:
                    if (
                        hashlib.file_digest(stream, "sha256").hexdigest()
                        != item["sha256"]
                    ):
                        raise ValueError(f"Archive verification failed: {relative}")
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    dependencies = run / "node_modules"
    pruned = False
    if prune and dependencies.is_dir():
        if dependencies.is_symlink():
            raise ValueError("Refusing to prune a symlinked dependency directory")
        shutil.rmtree(dependencies)
        pruned = True
    with target.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return {
        "run": run.name,
        "archive": str(target),
        "sha256": digest,
        "archive_bytes": target.stat().st_size,
        "verified_files": len(files),
        "dependencies_pruned": pruned,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", type=Path, nargs="+")
    parser.add_argument("--archive-dir", type=Path, required=True)
    parser.add_argument(
        "--prune-dependencies",
        action="store_true",
        help="Only use after confirming all selected run processes have exited",
    )
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    if args.manifest.exists():
        parser.error("Refusing to overwrite an existing evidence manifest")
    results = [
        archive(run, args.archive_dir, args.prune_dependencies) for run in args.runs
    ]
    args.manifest.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
