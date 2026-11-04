"""Audit actual stage requests without exposing their source contents or credentials."""

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path


def request_records(path):
    with Path(path).open() as stream:
        for line in stream:
            record = json.loads(line)
            if record.get("event") == "request":
                yield record


def audit(path):
    calls = []
    for record in request_records(path):
        messages = record["arguments"].get("messages", [])
        content = messages[-1].get("content", "") if messages else ""
        try:
            payload = json.loads(content)
        except (ValueError, TypeError):
            payload = {}
        files = payload.get("files", {})
        digest_counts = Counter()
        file_metrics = []
        for name, item in files.items():
            source = item.get("content") or ""
            digest = sha256(source.encode()).hexdigest()
            digest_counts[digest] += 1
            file_metrics.append(
                {
                    "path": name,
                    "characters": len(source),
                    "sha256": digest,
                    "writable": bool(item.get("writable")),
                }
            )
        calls.append(
            {
                "call_id": record["call_id"],
                "stage": record.get("stage"),
                "activity": record.get("activity"),
                "message_roles": [m["role"] for m in messages],
                "request_characters": len(json.dumps(messages, ensure_ascii=False)),
                "payload_keys": sorted(payload),
                "task_keys": sorted(payload.get("task", {})),
                "feedback_characters": len(
                    json.dumps(payload.get("feedback", []), ensure_ascii=False)
                ),
                "files": sorted(file_metrics, key=lambda x: -x["characters"]),
                "duplicate_file_content_groups": sum(
                    n > 1 for n in digest_counts.values()
                ),
            }
        )
    return {
        "source_sha256": sha256(Path(path).read_bytes()).hexdigest(),
        "measurement": "Characters, not tokenizer estimates. Path/size overlap does not prove irrelevance.",
        "calls": calls,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        json.dump(audit(args.log), stream, indent=2)
        stream.write("\n")
