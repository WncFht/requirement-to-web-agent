"""Audit complete SDK cache usage and replay alternative field order as characters, not token estimates."""

import argparse
from collections import Counter
from copy import deepcopy
import gzip
import json
from pathlib import Path


def common_prefix(left, right):
    lower, upper = 0, min(len(left), len(right))
    while lower < upper:
        middle = (lower + upper + 1) // 2
        if left[:middle] == right[:middle]:
            lower = middle
        else:
            upper = middle - 1
    return lower


def reorder(value, keys):
    return {**{key: value[key] for key in keys if key in value}, **value}


def alternative(arguments):
    result = deepcopy(arguments)
    messages = result.get("messages", [])
    if not messages or not isinstance(messages[-1].get("content"), str):
        return result
    payload = json.loads(messages[-1]["content"])
    if "event_id" in payload and "frontend_data" in payload:
        payload = reorder(
            payload,
            ("frontend_data", "page_inventory", "all_requirement_uses", "backend_apis"),
        )
    elif isinstance(payload.get("task"), dict) and "creation_scope" in payload["task"]:
        payload["task"] = reorder(
            payload["task"],
            (
                "creation_scope",
                "page_inventory",
                "frontend_data",
                "page_paths",
                "requirement",
            ),
        )
    messages[-1]["content"] = json.dumps(payload, ensure_ascii=False)
    assert json.loads(messages[-1]["content"]) == json.loads(
        arguments["messages"][-1]["content"]
    )
    return result


def analyze(path):
    rows, requests, responses = [], [], {}
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8-sig") as stream:
        for line in stream:
            row = json.loads(line)
            if row.get("event") == "request":
                requests.append(row)
            elif row.get("event") == "response":
                responses[row["call_id"]] = row
    previous, candidate_previous = [], []
    stages, activities = {}, {}
    for row in requests:
        arguments = row["arguments"]
        original = json.dumps(arguments.get("messages", []), ensure_ascii=False)
        candidate = json.dumps(
            alternative(arguments).get("messages", []), ensure_ascii=False
        )
        original_prefix = max(
            (common_prefix(original, before) for before in previous), default=0
        )
        candidate_prefix = max(
            (common_prefix(candidate, before) for before in candidate_previous),
            default=0,
        )
        previous.append(original)
        candidate_previous.append(candidate)
        response = responses.get(row["call_id"], {})
        usage = response.get("response", {}).get("usage") or {}
        values = {
            "calls": 1,
            "input_tokens": usage.get("prompt_tokens", 0) or 0,
            "cached_tokens": usage.get("prompt_cache_hit_tokens", 0) or 0,
            "actual_input_characters": len(original),
            "actual_longest_prior_prefix_characters": original_prefix,
            "reordered_longest_prior_prefix_characters": candidate_prefix,
        }
        kind = "creation" if " / Create " in row.get("activity", "") else "other"
        stages.setdefault(row["stage"], Counter()).update(values)
        activities.setdefault(kind, Counter()).update(values)
        rows.append(
            {
                "stage": row["stage"],
                "call_id": row["call_id"],
                "kind": kind,
                **values,
                "returned_usage": bool(usage),
                "ordering_changes_text": original != candidate,
            }
        )
    for group in [*stages.values(), *activities.values()]:
        group["cache_hit_ratio"] = (
            group["cached_tokens"] / group["input_tokens"]
            if group["input_tokens"]
            else None
        )
    return {
        "measurement": "SDK token cache usage plus longest matching serialized message prefix against ALL prior recorded requests. Reordered values/fields are identical. Prefix figures are characters, not tokens, not provider cache units, and not measured candidate cache hits or runtime savings.",
        "stages": stages,
        "activities": activities,
        "calls": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Refusing to overwrite prefix audit")
    args.output.write_text(
        json.dumps(analyze(args.log), ensure_ascii=False, indent=2) + "\n"
    )


if __name__ == "__main__":
    main()
