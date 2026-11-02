"""Verify the pinned upstream snapshot without network access or model credentials."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check(root=ROOT):
    record = json.loads((root / "upstream.json").read_text())
    directory = root / "upstream"
    actual = {
        path.relative_to(directory).as_posix(): hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        for path in directory.rglob("*")
        if path.is_file()
        and not any(
            part in {"__pycache__", ".pytest_cache", ".ruff_cache"}
            for part in path.relative_to(directory).parts
        )
    }
    expected = {item["path"]: item["sha256"] for item in record["files"]}
    expected.update(
        {name: change["sha256"] for name, change in record.get("patches", {}).items()}
    )
    if actual != expected:
        changed = sorted(
            name
            for name in actual.keys() | expected.keys()
            if actual.get(name) != expected.get(name)
        )
        raise ValueError("Pinned upstream files changed: " + ", ".join(changed))
    print(
        f"Upstream {record['revision'][:12]}: {len(actual)} files verified, {len(record.get('patches', {}))} recorded fixes"
    )
    return record


if __name__ == "__main__":
    check()
