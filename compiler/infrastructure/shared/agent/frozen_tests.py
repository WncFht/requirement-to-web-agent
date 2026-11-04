"""Seal generated suites before implementation; never accept later test edits."""

from hashlib import sha256
import json
from pathlib import Path, PurePosixPath

from infrastructure.utils.files import save_json


class FrozenTestViolation(ValueError):
    """A frozen suite or its receipt changed; preserve the failed run."""


_records = {}
RECEIPT = ".arc/frozen_tests.json"


def _state(output):
    root = Path(output).resolve()
    if root not in _records:
        receipt = root / RECEIPT
        _records[root] = json.loads(receipt.read_text()) if receipt.is_file() else {}
    return root, _records[root]


def _digest(root, relative):
    path = PurePosixPath(relative)
    if (path.is_absolute() or ".." in path.parts or str(path) != relative
            or not relative.startswith(("backend/tests/", "frontend/tests/"))
            or not relative.endswith((".test.ts", ".spec.ts"))):
        raise FrozenTestViolation("Not a generated test suite: " + relative)
    target = root / relative
    if (not target.is_file() or not target.resolve().is_relative_to(root)
            or any(part.is_symlink() for part in (target, *target.parents) if part != root)):
        raise FrozenTestViolation("Frozen test missing or linked: " + relative)
    return sha256(target.read_bytes()).hexdigest()


def is_frozen(output, relative):
    return relative in _state(output)[1]


def verify_frozen_tests(output):
    root, records = _state(output)
    if records:
        receipt = root / RECEIPT
        if not receipt.is_file() or json.loads(receipt.read_text()) != records:
            raise FrozenTestViolation("Frozen test receipt changed; use a new run directory")
    for relative, expected in records.items():
        if _digest(root, relative) != expected:
            raise FrozenTestViolation("Frozen test changed: " + relative)


def freeze_tests(output, paths):
    """Extend the receipt without replacing or unsealing an accepted suite."""
    root, records = _state(output)
    verify_frozen_tests(root)
    additions = {relative: _digest(root, relative) for relative in paths}
    updated = {**records, **additions}
    save_json(root / RECEIPT, updated)
    _records[root] = updated
    return dict(updated)


def archive_failed_tests(output, baseline, directory):
    """Retire only new failed-task suites after preserving their hashes and bytes."""
    root, records = _state(output)
    verify_frozen_tests(root)
    retired = {path: digest for path, digest in records.items() if path not in baseline}
    if retired:
        save_json(directory / "frozen_tests.json", retired)
        for path in retired:
            destination = directory / "files" / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((root / path).read_bytes())
        remaining = {path: digest for path, digest in records.items() if path in baseline}
        save_json(root / RECEIPT, remaining)
        _records[root] = remaining
