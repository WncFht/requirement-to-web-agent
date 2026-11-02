"""Failure-inclusive architecture metrics and per-attempt model/check failure locations."""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from coding_agent.trace import sha, usage_values
from scripts.audit_coding_campaign import cases, raw_usage
from scripts.summarize_factorial_campaign import wilson, describe


def load(path):
    return json.loads(Path(path).read_text())


def terminal_reason(record, directory):
    if record["success"]:
        return "COMPLETE_SUCCESS"
    generated = record["phases"]["generation"]
    if generated["status"] != "finished":
        return "GENERATION_" + generated["status"].upper()
    if generated["returncode"] != 0:
        result = directory / "output/.arc/agent/result.json"
        if result.exists():
            state = load(result)
            return state["phase"] + ":" + state["status"]
        log = directory / "generation.log"
        stages = re.findall(r"Stage (\d+)", log.read_text()) if log.exists() else []
        return "LEGACY_STAGE_" + (stages[-1] if stages else "UNKNOWN")
    for mode in ("fixed", "production"):
        phase = record["phases"].get(mode, {})
        if phase.get("status") == "error":
            return "EVALUATOR_ERROR:" + mode
        if record.get(mode) and record[mode]["status"] != "GREEN":
            return "ORACLE_FAILED:" + mode
    return "INCOMPLETE_EVIDENCE"


def trajectory(output, arm):
    path = output / ("model_calls.jsonl" if arm == "A" else ".arc/agent/events.jsonl")
    phases, actions, rejected, checks, models = (
        defaultdict(Counter),
        defaultdict(Counter),
        [],
        defaultdict(Counter),
        Counter(),
    )
    cache_complete = True
    if not path.exists():
        return {
            "phases": {},
            "actions": {},
            "rejected_actions": [],
            "checks": {},
            "models": {},
        }
    phase, turn, pending = "PREPARE_TESTS", None, 0
    for line in path.read_text().splitlines():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        kind = row.get("event") if arm == "A" else row.get("kind")
        if kind == "turn.start":
            phase, turn = row["phase"], row["turn"]
        if kind == "tests.freeze":
            phase = "IMPLEMENT"
        if kind in {"response", "model.response"}:
            response = (
                row.get("response", {})
                if arm == "A"
                else load(output / row["artifact"]["path"])
            )
            try:
                usage = usage_values(response.get("usage"))
            except ValueError:
                continue
            key = row.get("stage", "UNKNOWN") if arm == "A" else phase
            target = phases[key]
            target["calls"] += 1
            for field, value in usage.items():
                if value is not None:
                    target[field] += value
            cache_complete &= usage["cached_input_tokens"] is not None
            models[response.get("model", "UNKNOWN")] += 1
            pending += usage["total_tokens"]
        if kind == "action.end":
            key = (row.get("action") or "invalid_json") + ":" + row["status"]
            actions[key]["calls"] += 1
            actions[key]["associated_known_tokens"] += pending
            pending = 0
            if row["status"] in {"ERROR", "FAILED"}:
                observation = load(output / row["artifact"]["path"])
                rejected.append(
                    {
                        "turn": row["turn"],
                        "phase": phase,
                        "action": row.get("action"),
                        "summary": observation["summary"][:1500],
                        "artifact": row["artifact"]["path"],
                    }
                )
        if kind == "check.end":
            checks[row["name"]][row["status"]] += 1
            checks[row["name"]]["seconds"] += row["seconds"]
    return {
        "phases": dict(phases),
        "actions": dict(actions),
        "checks": dict(checks),
        "rejected_actions": rejected,
        "models": dict(models),
        "cache_usage_complete": cache_complete,
        "phase_scope": "Model response usage by phase; a finish call that freezes tests is preparation. Rejected-action costs are associated model usage, not a causal savings estimate.",
    }


def arm_summary(rows):
    successes = sum(r["success"] for r in rows)
    tokens = sum(r["tokens"] for r in rows)
    seconds = sum(r["wall_seconds"] for r in rows)
    unknown = sum(len(r["unknown_usage"]) for r in rows)
    return {
        "attempts": len(rows),
        "successes": successes,
        "wilson95": wilson(successes, len(rows)),
        "known_total_tokens": tokens,
        "unknown_usage_calls": unknown,
        "wall_seconds": seconds,
        "tokens_per_success": tokens / successes if successes and not unknown else None,
        "seconds_per_success": seconds / successes if successes else None,
        "all_attempt_tokens": describe([r["tokens"] for r in rows]),
        "all_attempt_seconds": describe([r["wall_seconds"] for r in rows]),
        "failed_known_tokens": sum(r["tokens"] for r in rows if not r["success"]),
        "terminal_reasons": dict(Counter(r["reason"] for r in rows)),
    }


def summarize(root):
    root = Path(root).resolve()
    protocol = load(root / "protocol.json")
    rows, missing, blocks = [], [], defaultdict(dict)
    for item in protocol["schedule"]:
        directory = root / "runs" / item["name"]
        if not (directory / "result.json").exists():
            missing.append(item["name"])
            continue
        record = load(directory / "result.json")
        usage, errors = raw_usage(directory / "output", item["arm"])
        row = item | {
            "success": record["success"],
            "reason": terminal_reason(record, directory),
            "tokens": usage["total_tokens"],
            "unknown_usage": usage["unknown"],
            "usage_errors": errors,
            "wall_seconds": record["wall_seconds"],
            "generation_seconds": record["phases"]["generation"]["seconds"],
            "trajectory": trajectory(directory / "output", item["arm"]),
            "failed_cases": {},
        }
        for mode in ("fixed", "production"):
            report = directory / mode / "playwright.json"
            if report.exists():
                row["failed_cases"][mode] = [
                    c
                    for c in cases(load(report))
                    if c["status"] != "expected" or c["results"] != ["passed"]
                ]
        rows.append(row)
        blocks[item["block"]][item["arm"]] = row
    pairs = [
        {
            "block": block,
            "A_success": group["A"]["success"],
            "B_success": group["B"]["success"],
            "B_minus_A_tokens": group["B"]["tokens"] - group["A"]["tokens"],
            "B_minus_A_seconds": group["B"]["wall_seconds"]
            - group["A"]["wall_seconds"],
        }
        for block, group in sorted(blocks.items())
        if set(group) == {"A", "B"}
    ]
    return {
        "task": protocol["task"],
        "kind": protocol["kind"],
        "sources": protocol["sources"],
        "protocol_sha256": sha(root / "protocol.json"),
        "analysis_script_sha256": sha(__file__),
        "complete": not missing,
        "missing_attempts": missing,
        "audit": load(root / "audit.json") if (root / "audit.json").exists() else None,
        "arms": {
            a: arm_summary([r for r in rows if r["arm"] == a])
            for a in sorted({r["arm"] for r in rows})
        },
        "pairs": pairs,
        "attempts": rows,
        "limits": "Attempts, not calls or individual test cases, are replicates. P1/P2/P3 and different revisions/tasks remain separate. Shorter failed runs are not successful delivery speedups. No invoice or provider/cache isolation claim. Visual similarity is not certified by the behavior oracle.",
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("campaign", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        p.error("Use a new analysis path")
    result = summarize(args.campaign)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("complete", "arms")}))
