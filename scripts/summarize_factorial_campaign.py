"""Failure-inclusive factorial results, blocked effects, and explicit small-sample uncertainty."""

import argparse
from itertools import product
import json
import math
from pathlib import Path
from statistics import mean, median


def wilson(successes, attempts):
    if not attempts:
        return None
    z = 1.959963984540054
    p = successes / attempts
    denominator = 1 + z * z / attempts
    middle = (p + z * z / (2 * attempts)) / denominator
    radius = (
        z
        * math.sqrt(p * (1 - p) / attempts + z * z / (4 * attempts * attempts))
        / denominator
    )
    return [max(0, middle - radius), min(1, middle + radius)]


def describe(values):
    return {
        "n": len(values),
        "mean": mean(values) if values else None,
        "median": median(values) if values else None,
        "min": min(values) if values else None,
        "max": max(values) if values else None,
    }


def quantile(values, probability):
    position = (len(values) - 1) * probability
    low = math.floor(position)
    high = math.ceil(position)
    return values[low] + (values[high] - values[low]) * (position - low)


def block_interval(values):
    if not values:
        return None
    # Exhaustive block bootstrap for the predeclared three blocks, not per-call pseudoreplication.
    sampled = sorted(mean(sample) for sample in product(values, repeat=len(values)))
    return {
        "mean": mean(values),
        "block_values": values,
        "bootstrap_95_percentile_interval": [
            quantile(sampled, 0.025),
            quantile(sampled, 0.975),
        ],
        "warning": "Exploratory with only three blocks: interval is unstable; it is not a guarantee of reproducible speedup or a large-sample significance test.",
    }


def cache_totals(records):
    inputs = sum(row["usage"]["totals"].get("prompt_tokens", 0) for row in records)
    cached = sum(
        row["usage"]["totals"].get("prompt_cache_hit_tokens", 0) for row in records
    )
    return {
        "input_tokens": inputs,
        "cached_input_tokens": cached,
        "uncached_input_tokens": inputs - cached,
        "weighted_hit_ratio": cached / inputs if inputs else None,
    }


def arm_summary(records):
    accepted = [row for row in records if row["success"]]
    failed = [row for row in records if not row["success"]]
    known_tokens = sum(row["usage"]["totals"].get("total_tokens", 0) for row in records)
    total_seconds = sum(row["attempt_wall_seconds"] for row in records)
    n = len(records)
    stages = {}
    for row in records:
        for name, values in row["usage"]["stages"].items():
            target = stages.setdefault(
                name,
                {
                    "input_tokens": 0,
                    "cached_input_tokens": 0,
                    "total_tokens": 0,
                    "calls": 0,
                },
            )
            for destination, source in (
                ("input_tokens", "prompt_tokens"),
                ("cached_input_tokens", "prompt_cache_hit_tokens"),
                ("total_tokens", "total_tokens"),
                ("calls", "calls"),
            ):
                target[destination] += values.get(source, 0)
    for values in stages.values():
        values["weighted_cache_hit_ratio"] = (
            values["cached_input_tokens"] / values["input_tokens"]
            if values["input_tokens"]
            else None
        )
    return {
        "attempts": n,
        "successes": len(accepted),
        "failures": len(failed),
        "success_rate": len(accepted) / n if n else None,
        "wilson_95_interval": wilson(len(accepted), n),
        "all_attempt_tokens": describe(
            [row["usage"]["totals"].get("total_tokens", 0) for row in records]
        ),
        "successful_attempt_tokens": describe(
            [row["usage"]["totals"].get("total_tokens", 0) for row in accepted]
        ),
        "all_attempt_wall_seconds": describe(
            [row["attempt_wall_seconds"] for row in records]
        ),
        "successful_generation_wall_seconds": describe(
            [row["phases"]["generation"]["seconds"] for row in accepted]
        ),
        "successful_complete_wall_seconds": describe(
            [row["attempt_wall_seconds"] for row in accepted]
        ),
        "failed_known_tokens": sum(
            row["usage"]["totals"].get("total_tokens", 0) for row in failed
        ),
        "failed_wall_seconds": sum(row["attempt_wall_seconds"] for row in failed),
        "known_tokens_per_accepted_app_including_failures": known_tokens / len(accepted)
        if accepted
        else None,
        "wall_seconds_per_accepted_app_including_failures": total_seconds
        / len(accepted)
        if accepted
        else None,
        "cache_all_attempts": cache_totals(records),
        "cache_successes_only": cache_totals(accepted),
        "unknown_usage_calls": sum(
            len(row["usage"]["calls_with_unknown_usage"]) for row in records
        ),
        "stages": stages,
    }


def metric(row, name):
    if name == "total_tokens":
        return row["usage"]["totals"].get("total_tokens", 0)
    if name == "generation_wall_seconds":
        return row["phases"]["generation"]["seconds"]
    if name == "uncached_input_tokens":
        total = row["usage"]["totals"]
        return total.get("prompt_tokens", 0) - total.get("prompt_cache_hit_tokens", 0)
    return row["attempt_wall_seconds"]


def effects(records, successful_only):
    blocks = {}
    for row in records:
        blocks.setdefault(row["block"], {})[row["arm"]] = row
    result = {}
    for name in (
        "total_tokens",
        "uncached_input_tokens",
        "generation_wall_seconds",
        "attempt_wall_seconds",
    ):
        values = {
            "context_main_effect": [],
            "prefix_main_effect": [],
            "interaction": [],
            "optimized_minus_control": [],
            "optimized_control_ratio": [],
        }
        excluded = []
        for block, group in sorted(blocks.items()):
            if (
                set(group) != {"00", "10", "01", "11"}
                or successful_only
                and not all(row["success"] for row in group.values())
            ):
                excluded.append(block)
                continue
            a, b, c, d = (metric(group[arm], name) for arm in ("00", "10", "01", "11"))
            values["context_main_effect"].append(((b + d) - (a + c)) / 2)
            values["prefix_main_effect"].append(((c + d) - (a + b)) / 2)
            values["interaction"].append(d - b - c + a)
            values["optimized_minus_control"].append(d - a)
            values["optimized_control_ratio"].append(d / a if a else 0)
        result[name] = {
            "effects": {key: block_interval(value) for key, value in values.items()},
            "excluded_blocks": excluded,
            "interpretation": "Negative additive effect favors enabled flag; ratio below one favors optimized. All-attempt shorter durations can reflect early failure, so no speedup claim without success-conditional and failure-inclusive cost agreement.",
        }
    return result


def summarize(root):
    protocol = json.loads((root / "protocol.json").read_text())
    records, missing = [], []
    for item in protocol["schedule"]:
        path = root / "runs" / item["name"] / "result.json"
        if not path.exists():
            missing.append(item["name"])
            continue
        row = json.loads(path.read_text())
        if (
            row["compiler_revision"] != protocol["compiler_revision"]
            or row["arm"] != item["arm"]
            or row["block"] != item["block"]
        ):
            raise ValueError("Result does not match predeclared source/schedule")
        records.append(row)
    arms = {
        arm: arm_summary([row for row in records if row["arm"] == arm])
        for arm in protocol["arms"]
    }
    return {
        "compiler_revision": protocol["compiler_revision"],
        "preregistered_attempts": len(protocol["schedule"]),
        "terminal_attempts": len(records),
        "missing_attempts": missing,
        "complete": not missing,
        "arms": arms,
        "blocked_all_attempt_effects": effects(records, False),
        "blocked_all_four_successful_effects": effects(records, True),
        "failures": [
            {
                "name": row["name"],
                "arm": row["arm"],
                "phases": row["phases"],
                "known_token_cost": row["usage"]["totals"].get("total_tokens", 0),
                "unknown_usage_calls": row["usage"]["calls_with_unknown_usage"],
                "fixed_stats": (row.get("fixed") or {}).get("stats"),
                "production_stats": (row.get("production") or {}).get("stats"),
            }
            for row in records
            if not row["success"]
        ],
        "limits": [
            "Fixed n=3 per arm, one teacher task and one provider; success intervals are wide. All failed attempts retained.",
            "Randomized serial blocking and constant source/env/dependencies control local overlap and setup, but provider cache state and server load cannot be pinned.",
            "Generated trajectories are random: factorial trials estimate full-pipeline treatment effects; paired request replay is separate mechanistic evidence.",
            "Token usage is not a money invoice; returned usage is a lower bound if calls lack usage. No assumed zero charge for failures.",
            "A 50% global cache ratio is assessed on actual pipeline input tokens; do not inflate it by retaining or adding useless context.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Refusing to overwrite a campaign analysis")
    args.output.write_text(
        json.dumps(summarize(args.campaign.resolve()), ensure_ascii=False, indent=2)
        + "\n"
    )


if __name__ == "__main__":
    main()
