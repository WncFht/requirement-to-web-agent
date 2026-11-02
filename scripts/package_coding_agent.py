"""Build a minimal platform ZIP from committed runtime sources, never local credentials."""

import argparse
import json
from pathlib import Path
import subprocess
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from coding_agent.trace import sha, json_write

ROOT = Path(__file__).resolve().parents[1]


def package(output):
    output = Path(output).resolve()
    if output.exists():
        raise ValueError("Refusing to overwrite platform package")
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    tracked = (
        subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
        .decode()
        .split("\0")
    )
    names = [
        n
        for n in tracked
        if n in {"main.py", "requirements.txt"}
        or n.startswith(("coding_agent/", "infrastructure/"))
    ]
    modified = subprocess.check_output(
        ["git", "diff", "HEAD", "--name-only"], cwd=ROOT, text=True
    ).splitlines()
    if set(modified) & set(names):
        raise ValueError("Commit runtime sources before packaging")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in names:
            path = ROOT / name
            if path.is_symlink():
                raise ValueError("No symlink in package")
            archive.write(path, name)
        archive.writestr("engine.json", json.dumps({"default": "coding"}))
    manifest = {
        "revision": revision,
        "zip_sha256": sha(output),
        "default_engine": "coding",
        "files": {name: sha(ROOT / name) for name in names},
        "engine.json": {"default": "coding"},
    }
    json_write(output.with_suffix(".json"), manifest)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    print(json.dumps(package(parser.parse_args().output), indent=2))
