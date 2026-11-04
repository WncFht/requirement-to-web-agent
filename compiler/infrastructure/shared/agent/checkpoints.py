"""Explicit immutable stage inputs, independent of successful-run receipts."""

from hashlib import sha256
import json
import os
from pathlib import Path

EXCLUDED = {"node_modules", ".git", ".env", "dist", "build", "coverage", "test-results", "__pycache__"}


def capture(application, destination, *, stage=None):
    """Copy source/config and .arc JSON only; dependencies and databases are not checkpoints."""
    application, destination = Path(application).resolve(), Path(destination).resolve()
    if destination == application or destination.is_relative_to(application):
        raise ValueError("Checkpoint must be outside the application")
    destination.mkdir(parents=True, exist_ok=False)
    records = {}
    sources = []
    for directory, names, files in os.walk(application, followlinks=False):
        names[:] = sorted(name for name in names if name not in EXCLUDED)
        sources.extend(Path(directory) / name for name in sorted(files))
    for source in sources:
        relative = source.relative_to(application)
        if set(relative.parts) & EXCLUDED or not source.is_file():
            continue
        if source.is_symlink():
            raise ValueError("Checkpoint source cannot contain symlinks: " + str(relative))
        if relative.parts[0] == ".arc":
            if len(relative.parts) != 2 or source.suffix != ".json":
                continue
        elif source.suffix not in {".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".css", ".html", ".json", ".sql", ".sh"}:
            continue
        data = source.read_bytes()
        target = destination / "application" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        records[relative.as_posix()] = sha256(data).hexdigest()
    manifest = {"version": 1, "stage": stage, "files": records,
        "scope": "Source/config and .arc JSON; no dependencies, database, credentials or trusted success"}
    (destination / "checkpoint.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def restore(checkpoint, destination):
    """Verify the complete checkpoint file set before restoring to a fresh workspace."""
    checkpoint, destination = Path(checkpoint).resolve(), Path(destination).resolve()
    manifest = json.loads((checkpoint / "checkpoint.json").read_text())
    actual = {}
    for source in (checkpoint / "application").rglob("*"):
        if source.is_symlink():
            raise ValueError("Checkpoint contains a symlink")
        if source.is_file():
            relative = source.relative_to(checkpoint / "application").as_posix()
            actual[relative] = sha256(source.read_bytes()).hexdigest()
    if actual != manifest["files"]:
        raise ValueError("Checkpoint hash/file-set mismatch")
    destination.mkdir(parents=True, exist_ok=False)
    for relative in actual:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((checkpoint / "application" / relative).read_bytes())
    # A replay must earn its own stage results; old GREEN reports are not reusable.
    for name in ("compilation.json", "ui_checks.json", "frontend_e2e.json"):
        (destination / ".arc" / name).unlink(missing_ok=True)
    return manifest
