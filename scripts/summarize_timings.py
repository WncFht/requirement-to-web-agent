"""Summarize inclusive wall-time spans without adding parents to their children."""

import argparse
from collections import Counter, defaultdict
import gzip
import json
import math
from pathlib import Path

CONTAINERS = {"entrypoint", "pipeline", "pipeline_stage", "stage_session", "stage_skip"}


def summarize(path):
    starts, ends, bad = {}, {}, []
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            try:
                row = json.loads(line)
                key = (row["trace_id"], row["span_id"])
                if row["version"] != 1 or row["event"] not in {"start", "end"}:
                    raise ValueError("unsupported timing event")
                if row["event"] == "end":
                    duration = row["elapsed_seconds"]
                    if (
                        isinstance(duration, bool)
                        or not isinstance(duration, (int, float))
                        or not math.isfinite(duration)
                        or duration < 0
                    ):
                        raise ValueError("invalid duration")
                target = starts if row["event"] == "start" else ends
                if key in target:
                    raise ValueError("duplicate event")
                target[key] = row
            except (ValueError, TypeError, KeyError) as error:
                bad.append({"line": number, "error_type": type(error).__name__})
    completed = []
    for key in starts.keys() & ends.keys():
        if any(
            starts[key].get(field) != ends[key].get(field)
            for field in ("kind", "parent_id", "stage", "pid", "name")
        ):
            bad.append({"span_id": key[1], "error_type": "MismatchedSpan"})
        else:
            completed.append(ends[key])
    completed.sort(key=lambda row: (row["timestamp"], row["span_id"]))
    traces = {}
    for trace in sorted({key[0] for key in starts} | {key[0] for key in ends}):
        rows = [row for row in completed if row["trace_id"] == trace]
        categories, stages = defaultdict(Counter), defaultdict(Counter)
        incomplete = [key[1] for key in starts.keys() - ends.keys() if key[0] == trace]
        for row in rows:
            if row["kind"] not in CONTAINERS:
                category = categories[row["kind"]]
                category.update(calls=1, seconds=row["elapsed_seconds"])
                category[row["status"]] += 1
            if row["kind"] == "pipeline_stage":
                stages[row["stage"]].update(attempts=1, seconds=row["elapsed_seconds"])
                stages[row["stage"]][row["status"]] += 1
        traces[trace] = {
            "entrypoint_seconds": [
                row["elapsed_seconds"] for row in rows if row["kind"] == "entrypoint"
            ],
            "pipeline_seconds": [
                row["elapsed_seconds"] for row in rows if row["kind"] == "pipeline"
            ],
            "stages": dict(stages),
            "categories": dict(categories),
            "skipped_stages": [
                row["stage"] for row in rows if row["kind"] == "stage_skip"
            ],
            "incomplete_span_ids": sorted(incomplete),
            "orphan_end_span_ids": sorted(
                key[1] for key in ends.keys() - starts.keys() if key[0] == trace
            ),
        }
    return {
        "schema_version": 1,
        "traces": traces,
        "malformed_or_duplicate_records": bad,
        "measurement": "Each span uses monotonic wall time; container durations include children. Category totals are cumulative command/SDK durations, not pipeline wall time or CPU time; concurrent work may overlap. SDK spans include SDK retries; outer backoff is separate. Missing ends are unknown, never zero.",
        "coverage": "Only instrumented code is counted. Stage/pipeline overhead, synthesis, validation, JSON serialization and uninstrumented commands remain outside categories. Fixed acceptance is measured separately when invoked under a timing session; it is not part of main.py wall time.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Refusing to overwrite a timing summary")
    result = summarize(args.log)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    if result["malformed_or_duplicate_records"]:
        parser.exit(
            1,
            "Timing summary contains invalid records; inspect diagnostics before using totals.\n",
        )


if __name__ == "__main__":
    main()
