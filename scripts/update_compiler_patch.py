"""Rebuild registered compiler diffs from a local pristine teacher Git checkout."""

import argparse
import difflib
from hashlib import sha256
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def update(teacher):
    manifest_path = ROOT / "compiler.json"
    record = json.loads(manifest_path.read_text())
    base = {entry["path"]: entry["sha256"] for entry in record["files"]}
    patch = []
    for name, entry in sorted(record["patches"].items()):
        new = (ROOT / "compiler" / name).read_bytes()
        old = (
            subprocess.check_output(
                ["git", "-C", str(teacher), "show", record["revision"] + ":" + name]
            )
            if name in base
            else b""
        )
        if name in base and sha256(old).hexdigest() != base[name]:
            raise ValueError("Pristine source hash mismatch: " + name)
        if not entry.get("reason"):
            raise ValueError("Register a reason before rebuilding: " + name)
        entry.update(original_sha256=base.get(name), sha256=sha256(new).hexdigest())
        patch.extend(
            difflib.unified_diff(
                old.decode().splitlines(keepends=True),
                new.decode().splitlines(keepends=True),
                fromfile="a/" + name if name in base else "/dev/null",
                tofile="b/" + name,
            )
        )
    manifest_path.write_text(json.dumps(record, indent=4) + "\n")
    (ROOT / "compiler.patch").write_bytes("".join(patch).encode())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--teacher-checkout", type=Path, required=True)
    update(parser.parse_args().teacher_checkout)
