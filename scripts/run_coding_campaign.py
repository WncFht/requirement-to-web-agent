"""Preregistered serial legacy/coding trials with immutable source and all failures retained."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
from time import monotonic, sleep

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from coding_agent.trace import json_write, sha, audit, file_manifest
from coding_agent.acceptance import evaluate
from infrastructure.utils.processes import start_process, stop_process
from run_factorial_campaign import (
    environment,
    safe_configuration,
    git,
    model_usage,
    fingerprint_tree,
    owned_output_processes,
)
from summarize_factorial_campaign import wilson


def usage(output, arm):
    if arm == "A":
        return model_usage(output / "model_calls.jsonl")
    events = output / ".arc/agent/events.jsonl"
    totals = {
        k: 0
        for k in (
            "prompt_tokens",
            "completion_tokens",
            "total_tokens",
            "cached_input_tokens",
            "uncached_input_tokens",
        )
    }
    unknown = []
    calls = 0
    if events.exists():
        for line in events.read_text().splitlines():
            try:
                r = json.loads(line)
            except ValueError:
                unknown.append("partial-event")
                continue
            if r.get("kind") == "model.response":
                calls += 1
                if not r.get("usage"):
                    unknown.append(r.get("call_id"))
                    continue
                for key in totals:
                    value = r["usage"].get(key)
                    if value is None and key in (
                        "cached_input_tokens",
                        "uncached_input_tokens",
                    ):
                        continue
                    totals[key] += value or 0
    return {
        "totals": totals,
        "response_count": calls,
        "calls_with_unknown_usage": unknown,
    }


def command_phase(
    command, source, env, log, timeout, output=None, arm=None, token_cap=None
):
    started = monotonic()
    status = "finished"
    with log.open("w") as stream:
        child = start_process(
            command, cwd=source, env=env, stdout=stream, stderr=stream
        )
        try:
            while child.poll() is None:
                if monotonic() - started > timeout:
                    status = "timeout"
                    stop_process(child)
                    break
                if (
                    output
                    and token_cap
                    and usage(output, arm)["totals"].get("total_tokens", 0) > token_cap
                ):
                    status = "token_budget"
                    stop_process(child)
                    break
                sleep(1)
        except BaseException:
            stop_process(child)
            raise
    return {
        "status": status,
        "returncode": child.returncode,
        "seconds": monotonic() - started,
    }


def summarize(root):
    protocol = json.loads((root / "protocol.json").read_text())
    rows = []
    for item in protocol["schedule"]:
        p = root / "runs" / item["name"] / "result.json"
        if p.exists():
            rows.append(json.loads(p.read_text()))
    result = {
        "complete": len(rows) == len(protocol["schedule"]),
        "attempts": len(rows),
        "registered_attempts": len(protocol["schedule"]),
        "arms": {},
    }
    for arm in sorted({r["arm"] for r in rows}):
        selected = [r for r in rows if r["arm"] == arm]
        successes = sum(r["success"] for r in selected)
        tokens = sum(r["usage"]["totals"].get("total_tokens", 0) for r in selected)
        seconds = sum(r["wall_seconds"] for r in selected)
        result["arms"][arm] = {
            "attempts": len(selected),
            "successes": successes,
            "wilson95": wilson(successes, len(selected)),
            "total_tokens": tokens,
            "wall_seconds": seconds,
            "tokens_per_success": tokens / successes if successes else None,
            "seconds_per_success": seconds / successes if successes else None,
        }
    result["results"] = rows
    return result


def campaign(args):
    root = args.output.resolve()
    candidate = args.candidate.resolve()
    baseline = args.baseline.resolve()
    if root.exists():
        raise ValueError("Use a new campaign directory")
    for source in (candidate, baseline):
        if git(source, "status", "--porcelain"):
            raise ValueError("Freeze clean sources before paid generation")
    env = environment(args.credentials.resolve(), args.node_bin.resolve())
    env.update(
        ARC_AGENT_MAX_TURNS="100",
        ARC_AGENT_MAX_TOKENS=str(args.token_cap),
        ARC_AGENT_MAX_SECONDS=str(args.seconds),
        ARC_AGENT_OUTPUT_TOKENS="8192",
        ARC_AGENT_TRANSPORT_RETRIES="1",
    )
    root.mkdir(parents=True)
    if args.kind == "p1":
        order = ["B", "B"]
    else:
        blocks = [["A", "B"] if i % 2 == 0 else ["B", "A"] for i in range(args.blocks)]
        random.Random(args.seed).shuffle(blocks)
        order = [arm for block in blocks for arm in block]
    schedule = [
        {"name": f"{i + 1:02d}-{arm}", "arm": arm, "block": i // 2 + 1}
        for i, arm in enumerate(order)
    ]
    protocol = {
        "version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "authorization": "User explicitly authorized completing the plan and paid generation on 2026-11-02; each batch remains bounded and failures retained.",
        "kind": args.kind,
        "sources": {
            "A": {
                "path": str(baseline),
                "revision": git(baseline, "rev-parse", "HEAD"),
            },
            "B": {
                "path": str(candidate),
                "revision": git(candidate, "rev-parse", "HEAD"),
            },
        },
        "runner_sha256": sha(__file__),
        "input_sha256": file_manifest(args.inputs.resolve()),
        "frozen_assertions": {
            p.relative_to(ROOT).as_posix(): sha(p)
            for p in [
                *(ROOT / "acceptance").glob("*"),
                *(ROOT / "input/tests").glob("*"),
            ]
            if p.is_file()
        },
        "configuration": safe_configuration(env),
        "generation_seconds": args.seconds,
        "per_attempt_token_cap": args.token_cap,
        "batch_token_cap": args.batch_cap,
        "schedule": schedule,
        "dependency_sha256": fingerprint_tree(args.dependencies.resolve())[0],
        "limitations": "Whole-architecture comparison. Generation randomness, provider routing and cache state not pinned. SDK usage is not invoice cost.",
    }
    json_write(root / "protocol.json", protocol)
    used = 0
    for item in schedule:
        if used >= args.batch_cap:
            raise ValueError("Batch token cap reached; retain incomplete schedule")
        arm = item["arm"]
        source = baseline if arm == "A" else candidate
        if git(source, "rev-parse", "HEAD") != protocol["sources"][arm][
            "revision"
        ] or git(source, "status", "--porcelain"):
            raise ValueError("Measured source changed")
        runroot = root / "runs" / item["name"]
        output = runroot / "output"
        output.mkdir(parents=True)
        prep = monotonic()
        shutil.copytree(
            args.dependencies.resolve(), output / "node_modules", symlinks=True
        )
        prepared = monotonic() - prep
        treatment = env | {
            "ARC_AGENT_ENGINE": "coding" if arm == "B" else "legacy",
            "ARC_EVENT_CONTEXT": "1",
            "ARC_CACHE_PREFIX": "1",
        }
        record = item | {
            "revision": protocol["sources"][arm]["revision"],
            "started_utc": datetime.now(timezone.utc).isoformat(),
            "snapshot_seconds": prepared,
            "phases": {},
            "fixed": None,
            "production": None,
            "success": False,
        }
        json_write(runroot / "experiment.json", record)
        started = monotonic()
        print(json.dumps({"event": "attempt.start", **item}), flush=True)
        generation = command_phase(
            [
                sys.executable,
                "-u",
                "main.py",
                str(args.inputs.resolve()),
                "-o",
                str(output),
            ],
            source,
            treatment,
            runroot / "generation.log",
            args.seconds + 15,
            output,
            arm,
            args.token_cap,
        )
        record["phases"]["generation"] = generation
        if generation["returncode"] == 0 and generation["status"] == "finished":
            for mode in ("fixed", "production"):
                phase_started = monotonic()
                try:
                    adapter = (
                        json.loads((runroot / "fixed/adapter.json").read_text())
                        if mode == "production"
                        else None
                    )
                    report = evaluate(output, runroot / mode, mode, adapter)
                    record[mode] = report
                    record["phases"][mode] = {
                        "status": "finished",
                        "returncode": 0 if report["status"] == "GREEN" else 1,
                        "seconds": monotonic() - phase_started,
                    }
                except Exception as error:
                    record["phases"][mode] = {
                        "status": "error",
                        "returncode": 1,
                        "seconds": monotonic() - phase_started,
                        "error": str(error).replace(
                            env.get("OPENAI_API_KEY", "<none>"), "[redacted]"
                        ),
                    }
                if not record.get(mode) or record[mode]["status"] != "GREEN":
                    break
        record["usage"] = usage(output, arm)
        used += record["usage"]["totals"].get("total_tokens", 0)
        record["wall_seconds"] = monotonic() - started
        record["completed_utc"] = datetime.now(timezone.utc).isoformat()
        record["success"] = all(
            record.get(k) and record[k]["status"] == "GREEN"
            for k in ("fixed", "production")
        )
        record["source_unchanged"] = git(source, "rev-parse", "HEAD") == record[
            "revision"
        ] and not git(source, "status", "--porcelain")
        record["sealed_application"] = file_manifest(output, logs=True)
        if arm == "B" and (output / ".arc/agent/result.json").exists():
            record["agent_audit"] = audit(output)
        json_write(runroot / "result.json", record)
        json_write(root / "analysis.json", summarize(root))
        print(
            json.dumps(
                {
                    "event": "attempt.end",
                    "name": item["name"],
                    "success": record["success"],
                    "tokens": record["usage"]["totals"].get("total_tokens", 0),
                    "seconds": record["wall_seconds"],
                }
            ),
            flush=True,
        )
        leftovers = owned_output_processes(output)
        if leftovers:
            raise ValueError(
                "Owned application processes remain; stop before next attempt"
            )
    json_write(
        root / "complete.json",
        {
            "attempts": len(schedule),
            "tokens": used,
            "completed_utc": datetime.now(timezone.utc).isoformat(),
        },
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--candidate", type=Path, required=True)
    p.add_argument("--baseline", type=Path, required=True)
    p.add_argument("--credentials", type=Path, required=True)
    p.add_argument("--node-bin", type=Path, required=True)
    p.add_argument("--dependencies", type=Path, required=True)
    p.add_argument("--inputs", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--kind", choices=("p1", "p2", "p3"), required=True)
    p.add_argument("--blocks", type=int, default=4)
    p.add_argument("--seed", type=int, default=4810)
    p.add_argument("--seconds", type=int, default=1200)
    p.add_argument("--token-cap", type=int, default=2500000)
    p.add_argument("--batch-cap", type=int, default=25000000)
    campaign(p.parse_args())
