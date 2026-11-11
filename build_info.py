"""Identify shipped source independently of the runner's Git checkout."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

PACKAGE_ENTRIES = (
    "main.py", "arc_adapter.py", "progress.py", "build_info.py", "engine_source.py",
    "requirements.txt", "pytest.ini", ".env.example", "README.md",
    "scripts", "tests", "web_template", "vendor",
)
EXCLUDED = {".env", ".DS_Store", "__pycache__", "node_modules", "dist", ".git", ".pytest_cache", ".ruff_cache", "build"}


def source_files(root: Path) -> dict[str, bytes]:
    """One snapshot supplies both archive bytes and their fingerprint."""
    files = {}
    for name in PACKAGE_ENTRIES:
        entry = root / name
        for path in [entry] if entry.is_file() else sorted(entry.rglob("*")):
            if (not path.is_file() or EXCLUDED.intersection(path.relative_to(root).parts)
                    or any(part.endswith(".egg-info") for part in path.relative_to(root).parts)):
                continue
            if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
                raise ValueError(f"Package source must be a regular local file: {path}")
            files[path.relative_to(root).as_posix()] = path.read_bytes()
    return files


def fingerprint(files: dict[str, bytes]) -> tuple[dict[str, str], str]:
    hashes = {name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())}
    encoded = json.dumps(hashes, sort_keys=True, separators=(",", ":")).encode()
    return hashes, hashlib.sha256(encoded).hexdigest()


def git_identity(root: Path) -> dict:
    def git(*args: str) -> str:
        return subprocess.check_output(
            ["git", "-C", str(root), *args], stderr=subprocess.DEVNULL,
            text=True, timeout=10,
        ).strip()

    unknown = {"commit": None, "tags": [], "branch": None, "dirty": None}
    # A deployed ZIP may live inside an unrelated Git repository.
    if not (root / ".git").exists():
        return unknown
    try:
        commit = git("rev-parse", "HEAD")
        tags = git("tag", "--points-at", "HEAD").splitlines()
        branch = git("rev-parse", "--abbrev-ref", "HEAD")
        status = git("status", "--porcelain", "--untracked-files=all", "--", *PACKAGE_ENTRIES)
        return {"commit": commit, "tags": tags, "branch": None if branch == "HEAD" else branch,
                "dirty": bool(status)}
    except (OSError, subprocess.SubprocessError):
        return unknown


def create_build_info(root: Path, files: dict[str, bytes] | None = None) -> dict:
    hashes, digest = fingerprint(source_files(root) if files is None else files)
    return {"schema_version": 1, "built_at": datetime.now(UTC).isoformat(),
            **git_identity(root), "source_sha256": digest, "files": hashes}


def runtime_build_info(root: Path) -> dict:
    """Prefer frozen package provenance; verify it against actual source."""
    packaged = root / "build_info.json"
    if not packaged.exists():
        return {**create_build_info(root), "origin": "checkout" if (root / ".git").exists()
                else "unversioned", "matches_build": None}
    frozen = json.loads(packaged.read_text(encoding="utf-8"))
    hashes, digest = fingerprint(source_files(root))
    expected = frozen["files"]
    changed = sorted(name for name in hashes.keys() | expected.keys()
                     if hashes.get(name) != expected.get(name))
    return {**frozen, "origin": "package", "matches_build": not changed,
            "runtime_source_sha256": digest, "changed_files": changed}


def write_run_build_info(root: Path, output: Path, *, configuration: dict) -> dict:
    info = {**runtime_build_info(root), "run_configuration": configuration}
    details = output / ".arc_adapter"
    details.mkdir(parents=True, exist_ok=True)
    (details / "build_info.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    return info
