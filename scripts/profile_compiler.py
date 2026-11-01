"""Profile audited model costs and replay creation payload scope without model calls."""

import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from infrastructure.stages.frontend.interactions.creation_context import (
    creation_context,
)


def size(value):
    return len(json.dumps(value, ensure_ascii=False))


def profile(path):
    """Count only SDK responses; unknown in-flight/error request usage stays unknown."""
    requests, responses = {}, {}
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8-sig") as stream:
        for line in stream:
            row = json.loads(line)
            if row["event"] == "request":
                requests[row["call_id"]] = row
            elif row["event"] == "response":
                responses[row["call_id"]] = row
    stages = defaultdict(Counter)
    groups = defaultdict(Counter)
    replay = []
    for call_id, response in responses.items():
        usage = response["response"].get("usage")
        if not isinstance(usage, dict):
            raise ValueError("Returned SDK response lacks usage")
        request = requests[call_id]
        activity = request.get("activity", "")
        kind = (
            "creation"
            if " / Create " in activity
            else "test_generation"
            if " / Test Generation" in activity
            else "test_review"
            if "contradiction review" in activity
            else "implementation_or_repair"
            if "Implementation" in activity
            else "design_or_other"
        )
        values = {
            key: usage.get(key, 0) or 0
            for key in (
                "prompt_tokens",
                "completion_tokens",
                "total_tokens",
                "prompt_cache_hit_tokens",
            )
        }
        values.update(calls=1, model_seconds=response.get("elapsed_seconds", 0))
        stages[response["stage"]].update(values)
        groups[kind].update(values)
        arguments = request.get("arguments", {})
        message = arguments.get("messages", [{}])[-1].get("content")
        if kind != "creation" or not isinstance(message, str):
            continue
        payload = json.loads(message)
        task = payload.get("task", {})
        # Legacy slim creation selects exactly one event; final repairs keep all.
        targets = task.get("target_event_ids", [])
        if len(targets) != 1 or "page_subtrees" not in task or "new_file" not in task:
            continue
        event_id = targets[0]
        scoped = creation_context(
            task, event_id, task["implementation_paths"], task["page_paths"]
        )
        scoped["new_file"] = task["new_file"]
        files = {
            key: value
            for key, value in payload["files"].items()
            if key in {"frontend/src/ui-runtime.ts", "frontend/src/ui-api.ts"}
        }
        after = {**payload, "task": scoped, "files": files}
        replay.append(
            {
                "call_id": call_id,
                "event_id": event_id,
                "before_payload_characters": size(payload),
                "after_payload_characters": size(after),
                "actual_before_prompt_tokens": usage["prompt_tokens"],
                "after_prompt_tokens": None,
                "before_sections_characters": {
                    key: size(value) for key, value in task.items()
                },
            }
        )
    totals = Counter()
    for values in stages.values():
        totals.update(values)
    return {
        "log_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "measurement": "SDK usage once per returned call; cumulative request time is not pipeline wall time",
        "totals": dict(totals),
        "stages": dict(stages),
        "groups": dict(groups),
        "requests_without_returned_usage": sorted(set(requests) - set(responses)),
        "creation_replay": replay,
        "replay_scope": "Same recorded calls, payload character counts only; no model execution, output or inferred token savings",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Refusing to overwrite a profile")
    args.output.write_text(json.dumps(profile(args.log), indent=2) + "\n")


if __name__ == "__main__":
    main()
