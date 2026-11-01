"""Aggregate audited SDK responses once; HTTP mirrors are not extra model calls."""

import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path

FIELDS = (
    "prompt_tokens",
    "completion_tokens",
    "total_tokens",
    "prompt_cache_hit_tokens",
    "prompt_cache_miss_tokens",
)


def summarize(path: Path) -> dict:
    stages = defaultdict(Counter)
    events = Counter()
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            record = json.loads(line)
            events[record["event"]] += 1
            if record["event"] != "response":
                continue
            usage = record["response"].get("usage")
            if not isinstance(usage, dict):
                raise ValueError(
                    "SDK response has no usage; token totals are incomplete"
                )
            stage = stages[record["stage"]]
            stage["calls"] += 1
            for key in FIELDS:
                stage[key] += usage.get(key, 0) or 0
            stage["reasoning_tokens"] += (
                usage.get("completion_tokens_details") or {}
            ).get("reasoning_tokens", 0) or 0
            stage["model_seconds"] += record.get("elapsed_seconds", 0) or 0
    totals = Counter()
    for stage in stages.values():
        totals.update(stage)

    def metrics(values):
        return dict(values) | {
            "input_cache_hit_ratio": (
                values["prompt_cache_hit_tokens"] / values["prompt_tokens"]
                if values["prompt_tokens"]
                else None
            )
        }

    with path.open("rb") as raw:
        digest = hashlib.file_digest(raw, "sha256").hexdigest()
    return {
        "log": str(path),
        "log_sha256": digest,
        "events": dict(events),
        "totals": metrics(totals),
        "stages": {name: metrics(value) for name, value in sorted(stages.items())},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", type=Path, nargs="+")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps([summarize(path) for path in args.logs], indent=2) + "\n"
    if args.output:
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")


if __name__ == "__main__":
    main()
