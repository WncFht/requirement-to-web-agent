"""Append-only events, content-addressed attachments and independently auditable seals."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from time import monotonic
from uuid import uuid4


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def json_write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


def file_manifest(root, *, logs=False):
    result = {}
    for path in sorted(Path(root).rglob("*")):
        relative = path.relative_to(root)
        if any(
            p in {"node_modules", ".git", "__pycache__", "test-results"}
            for p in relative.parts
        ):
            continue
        if relative.parts[:2] == ("backend", "data"):
            continue
        if relative.parts[0] == ".arc" and not logs:
            continue
        if path.is_symlink():
            raise ValueError(f"Symlink in auditable application: {relative}")
        if path.is_file() and path.name not in {
            "artifact-manifest.json",
            "result.json",
        }:
            result[relative.as_posix()] = sha(path)
    return result


def fingerprint(files):
    return hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()


def usage_values(usage):
    required = {"prompt_tokens", "completion_tokens", "total_tokens"}
    if not isinstance(usage, dict) or any(
        type(usage.get(k)) is not int or usage[k] < 0 for k in required
    ):
        raise ValueError("Missing or invalid required SDK usage fields")
    if usage["total_tokens"] != usage["prompt_tokens"] + usage["completion_tokens"]:
        raise ValueError("Inconsistent SDK token total")
    result = {k: usage[k] for k in required}
    details = usage.get("prompt_tokens_details") or {}
    cached = usage.get("prompt_cache_hit_tokens", details.get("cached_tokens"))
    result["cached_input_tokens"] = cached
    result["uncached_input_tokens"] = (
        usage["prompt_tokens"] - cached if type(cached) is int else None
    )
    if cached is not None and (
        type(cached) is not int or not 0 <= cached <= usage["prompt_tokens"]
    ):
        raise ValueError("Invalid cached input token count")
    return result


class Trace:
    def __init__(self, output):
        self.output = Path(output)
        self.root = self.output / ".arc/agent"
        self.root.mkdir(parents=True, exist_ok=False)
        self.run_id = uuid4().hex
        self.started = monotonic()
        self.seq = 0
        self.tokens = 0
        self.calls = 0
        self.evidence_complete = True

    def emit(self, kind, **fields):
        self.seq += 1
        row = {
            "schema_version": 1,
            "run_id": self.run_id,
            "seq": self.seq,
            "utc": datetime.now(timezone.utc).isoformat(),
            "offset_seconds": monotonic() - self.started,
            "kind": kind,
            **fields,
        }
        with (self.root / "events.jsonl").open("a") as stream:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        return row

    def artifact(self, label, value):
        name = f"artifacts/{self.seq + 1:05d}-{label}.json"
        path = self.root / name
        json_write(path, value)
        return {"path": path.relative_to(self.output).as_posix(), "sha256": sha(path)}

    def response(self, call_id, response):
        attachment = self.artifact("response", response)
        try:
            usage = usage_values(response.get("usage"))
        except ValueError:
            self.evidence_complete = False
            self.emit(
                "model.response", call_id=call_id, artifact=attachment, usage=None
            )
            raise
        self.calls += 1
        self.tokens += usage["total_tokens"]
        self.emit("model.response", call_id=call_id, artifact=attachment, usage=usage)
        return usage

    def seal(self, status, **fields):
        self.emit("run.end", status=status)
        files = file_manifest(self.output, logs=True)
        manifest = self.root / "artifact-manifest.json"
        json_write(manifest, {"version": 1, "files": files})
        result = {
            "version": 1,
            "run_id": self.run_id,
            "status": status,
            "model_calls": self.calls,
            "total_tokens": self.tokens,
            "wall_seconds": monotonic() - self.started,
            "evidence_complete": self.evidence_complete,
            "manifest_sha256": sha(manifest),
            **fields,
        }
        json_write(self.root / "result.json", result)
        return result


def audit(output):
    root = Path(output) / ".arc/agent"
    result = json.loads((root / "result.json").read_text())
    manifest = json.loads((root / "artifact-manifest.json").read_text())
    issues = []
    if sha(root / "artifact-manifest.json") != result["manifest_sha256"]:
        issues.append("Manifest changed")
    actual = file_manifest(Path(output), logs=True)
    if manifest["files"] != actual:
        issues.append("Application, tests, configuration or original evidence changed")
    requests, responses, pending_checks = set(), set(), set()
    tokens = 0
    for number, line in enumerate((root / "events.jsonl").read_text().splitlines(), 1):
        row = json.loads(line)
        if row["seq"] != number or row["run_id"] != result["run_id"]:
            issues.append("Event sequence or run identity changed")
        if row["kind"] == "model.request":
            if row["call_id"] in requests:
                issues.append("Duplicate model request")
            requests.add(row["call_id"])
        if row["kind"] == "model.response":
            if row["call_id"] in responses:
                issues.append("Duplicate model response")
            responses.add(row["call_id"])
            raw = json.loads((Path(output) / row["artifact"]["path"]).read_text())
            try:
                values = usage_values(raw.get("usage"))
                if row["usage"] != values:
                    issues.append("SDK usage differs from raw response")
                tokens += values["total_tokens"]
            except ValueError:
                issues.append("Unknown SDK usage")
        if row["kind"] == "check.start":
            pending_checks.add(row["check_id"])
        if row["kind"] == "check.end":
            pending_checks.discard(row["check_id"])
    if requests != responses:
        issues.append("Unpaired model request/response")
    if pending_checks:
        issues.append("Unfinished checks")
    if tokens != result["total_tokens"] or len(responses) != result["model_calls"]:
        issues.append("Derived usage totals differ")
    return {"valid": not issues, "issues": issues, "result": result}
