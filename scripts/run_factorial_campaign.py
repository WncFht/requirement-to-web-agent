"""Predeclare and run serial, blocked 2x2 compiler trials without changing the measured revision."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
from time import monotonic

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from infrastructure.utils.files import save_json
from infrastructure.utils.processes import start_process, stop_process

ARMS = {"00": (0, 0), "10": (1, 0), "01": (0, 1), "11": (1, 1)}
MODEL_SETTINGS = (
    "MODEL",
    "VISUAL_MODEL",
    "OPENAI_BASE_URL",
    "VISUAL_BASE_URL",
    "MAX_OUTPUT_TOKENS",
)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def git(source, *args):
    return subprocess.check_output(["git", *args], cwd=source, text=True).strip()


def fingerprint_tree(root):
    """Hash immutable dependency bytes and relative symlink targets, never private configuration."""
    hashes = {}
    for directory, directories, filenames in os.walk(root, followlinks=False):
        for name in list(directories):
            path = Path(directory) / name
            if path.is_symlink():
                hashes[path.relative_to(root).as_posix()] = "symlink:" + os.readlink(
                    path
                )
                directories.remove(name)
        for name in filenames:
            path = Path(directory) / name
            hashes[path.relative_to(root).as_posix()] = (
                "symlink:" + os.readlink(path) if path.is_symlink() else sha(path)
            )
    return hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest(), len(
        hashes
    )


def schedule(blocks=3, seed=4810):
    rng = random.Random(seed)
    order = list(ARMS)
    rng.shuffle(order)
    # Rotating a shuffled base gives every arm different positions across blocks.
    return [
        {
            "block": block + 1,
            "position": position + 1,
            "arm": arm,
            "name": f"b{block + 1}-{position + 1}-{arm}",
        }
        for block in range(blocks)
        for position, arm in enumerate(order[block % 4 :] + order[: block % 4])
    ]


def environment(source, node_bin):
    values = {**dotenv_values(source / ".env"), **os.environ}
    env = {key: str(value) for key, value in values.items() if value is not None}
    for name in list(env):
        if name.startswith("ARC_"):
            env.pop(name)
    env.update(
        {
            "PATH": str(node_bin) + os.pathsep + os.environ["PATH"],
            "ARC_DISABLE_THINKING": "1",
            "ARC_MODEL_TRANSPORT_RETRIES": "4",
            "ARC_DISABLE_TIMING": "0",
            "ARC_FULL_CONTEXT": "0",
            "ARC_FULL_FEEDBACK": "0",
            "ARC_REUSE_E2E_TESTS": "0",
            "ARC_UI_DESIGN_FRESH": "1",
            "npm_config_registry": "https://registry.npmmirror.com",
            "PLAYWRIGHT_DOWNLOAD_HOST": "https://npmmirror.com/mirrors/playwright",
            "npm_config_nodedir": str(node_bin.parent),
        }
    )
    # Every legacy bypass must be explicitly disabled in this frozen revision.
    import re

    for path in [*source.glob("*.py"), *(source / "infrastructure").rglob("*.py")]:
        for name in re.findall(
            r"""os\.getenv\(\s*["'](ARC_LEGACY_[A-Z0-9_]+)["']""",
            path.read_text(encoding="utf-8-sig"),
        ):
            env[name] = "0"
    return env


def safe_configuration(env):
    return {
        key: env.get(key)
        for key in sorted(
            set(MODEL_SETTINGS)
            | {key for key in env if key.startswith("ARC_")}
            | {"npm_config_registry", "npm_config_nodedir", "PLAYWRIGHT_DOWNLOAD_HOST"}
        )
    }


def model_usage(path):
    """Retain partial audit uncertainty on killed/failed calls; count SDK responses once."""
    requests, responses, errors, malformed = {}, {}, {}, []
    if path.exists():
        for index, line in enumerate(
            path.read_text(encoding="utf-8-sig").splitlines(), 1
        ):
            try:
                row = json.loads(line)
                event = row.get("event")
                if event in {"request", "response", "error"}:
                    {"request": requests, "response": responses, "error": errors}[
                        event
                    ][row["call_id"]] = row
            except (ValueError, KeyError, TypeError):
                malformed.append(index)
    totals, stages = Counter(), {}
    absent = []
    for call, row in responses.items():
        usage = row.get("response", {}).get("usage")
        if not isinstance(usage, dict):
            absent.append(call)
            continue
        values = {
            key: usage.get(key, 0) or 0
            for key in (
                "prompt_tokens",
                "completion_tokens",
                "total_tokens",
                "prompt_cache_hit_tokens",
                "prompt_cache_miss_tokens",
            )
        }
        values.update(calls=1, sdk_seconds=row.get("elapsed_seconds", 0))
        totals.update(values)
        stages.setdefault(row.get("stage", "UNKNOWN"), Counter()).update(values)
    totals["sdk_error_seconds"] = sum(
        row.get("elapsed_seconds", 0) or 0 for row in errors.values()
    )
    return {
        "totals": dict(totals),
        "stages": {key: dict(value) for key, value in stages.items()},
        "request_count": len(requests),
        "response_count": len(responses),
        "sdk_error_count": len(errors),
        "calls_with_unknown_usage": sorted(
            (set(requests) - set(responses)) | set(absent)
        ),
        "malformed_lines": malformed,
        "log_sha256": sha(path) if path.exists() else None,
        "cost_scope": "Returned SDK token usage only; missing/error call usage and provider invoice cost remain unknown, never assumed free.",
    }


def read_summary(path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))


def phase(command, source, env, log, timeout):
    started = monotonic()
    with log.open("w", encoding="utf-8") as stream:
        child = start_process(
            command, cwd=source, env=env, stdout=stream, stderr=stream
        )
        status, code = "finished", None
        try:
            code = child.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            status = "timeout"
            stop_process(child)
            code = child.returncode
        except BaseException:
            stop_process(child)
            raise
    return {
        "status": status,
        "returncode": code,
        "seconds": monotonic() - started,
        "timeout_seconds": timeout,
    }


def seal(source, protocol, env):
    if git(source, "rev-parse", "HEAD") != protocol["compiler_revision"] or git(
        source, "status", "--porcelain"
    ):
        raise ValueError(
            "Measured compiler changed; stop the campaign without replacing results"
        )
    if safe_configuration(env) != protocol["configuration"]:
        raise ValueError("Effective benchmark configuration changed")
    for relative, expected in protocol["frozen_files"].items():
        if sha(source / relative) != expected:
            raise ValueError(f"Frozen input/acceptance changed: {relative}")


def owned_output_processes(output):
    """Linux diagnostic/cleanup identities only, never unrelated command/environment content."""
    result = []
    for proc in Path("/proc").iterdir():
        if not proc.name.isdecimal() or int(proc.name) == os.getpid():
            continue
        try:
            cwd = (proc / "cwd").resolve()
            if cwd == output or cwd.is_relative_to(output):
                result.append(int(proc.name))
        except OSError:
            pass
    return result


def run_one(source, root, protocol, item, env):
    seal(source, protocol, env)
    output = root / "runs" / item["name"]
    if output.exists():
        raise ValueError(f"Refusing to restart/overwrite attempt: {output}")
    output.mkdir(parents=True)
    # All arms start from the same warm dependency snapshot; preparation is timed separately.
    preparation = monotonic()
    shutil.copytree(root / "dependencies", output / "node_modules", symlinks=True)
    prepared = monotonic() - preparation
    treatment = env | {
        "ARC_EVENT_CONTEXT": str(ARMS[item["arm"]][0]),
        "ARC_CACHE_PREFIX": str(ARMS[item["arm"]][1]),
    }
    record = {
        **item,
        "compiler_revision": protocol["compiler_revision"],
        "configuration": safe_configuration(treatment),
        "snapshot_preparation_seconds": prepared,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "host_load_before": list(os.getloadavg()),
        "phases": {},
    }
    save_json(output / "experiment.json", record)
    commands = [
        (
            "generation",
            [sys.executable, "-u", "main.py", "input", "-o", str(output)],
            protocol["generation_timeout_seconds"],
        ),
        (
            "fixed",
            [
                sys.executable,
                "scripts/accept_teacher.py",
                str(output),
                "--attempt",
                "campaign",
            ],
            900,
        ),
        (
            "production",
            [
                sys.executable,
                "scripts/accept_production.py",
                str(output),
                "--attempt",
                "campaign",
                "--fixed-attempt",
                "campaign",
            ],
            900,
        ),
    ]
    started = monotonic()
    for name, command, timeout in commands:
        value = phase(command, source, treatment, output / f"{name}.log", timeout)
        record["phases"][name] = value
        save_json(output / "experiment.json", record)
        if value["status"] != "finished" or value["returncode"] != 0:
            break
    record["attempt_wall_seconds"] = monotonic() - started
    record["usage"] = model_usage(output / "model_calls.jsonl")
    record["gates"] = {
        name: read_summary(output / ".arc" / f"{name}.json")
        for name in ("backend_tdd", "ui_checks", "frontend_e2e")
    }
    fixed = read_summary(output / ".arc/teacher-acceptance/campaign/summary.json")
    production = read_summary(
        output / ".arc/production-acceptance/campaign/summary.json"
    )
    record["fixed"] = fixed
    record["production"] = production
    record["success"] = success(record)
    record["completed_utc"] = datetime.now(timezone.utc).isoformat()
    record["host_load_after"] = list(os.getloadavg())
    # Services left by a failed attempt must not distort the next serial trial.
    leftovers = owned_output_processes(output)
    if leftovers:
        import signal

        for pid in leftovers:
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        from time import sleep

        sleep(1)
        still_owned = owned_output_processes(output)
        for pid in still_owned:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        record["owned_cleanup"] = {"term_pids": leftovers, "kill_pids": still_owned}
    record["post_run_source_integrity"] = "PASSED"
    seal(source, protocol, env)
    save_json(output / "result.json", record)
    return record


def success(record):
    if len(record["phases"]) != 3 or any(
        value["status"] != "finished" or value["returncode"] != 0
        for value in record["phases"].values()
    ):
        return False
    if not all(
        value and value.get("status") == "GREEN" for value in record["gates"].values()
    ):
        return False
    fixed, production = record.get("fixed"), record.get("production")
    for value in (fixed, production):
        if (
            not value
            or value.get("status") != "GREEN"
            or value.get("stats", {}).get("expected") != 14
            or any(
                value.get("stats", {}).get(key)
                for key in ("unexpected", "skipped", "flaky")
            )
        ):
            return False
    return fixed.get("all_preserved_gates_green", False) and fixed.get(
        "production_build_passed", False
    )


def initialize(source, root, dependencies, env, blocks, generation_timeout):
    if root.exists():
        raise ValueError(
            "Campaign already exists; use --resume only after verifying its runner has stopped"
        )
    root.mkdir(parents=True)
    revision = git(source, "rev-parse", "HEAD")
    if git(source, "status", "--porcelain"):
        raise ValueError("Freeze a clean measured compiler checkout")
    frozen = {
        path.relative_to(source).as_posix(): sha(path)
        for folder in ("input", "acceptance")
        for path in (source / folder).rglob("*")
        if path.is_file()
    }
    source_hash, count = fingerprint_tree(dependencies)
    shutil.copytree(dependencies, root / "dependencies", symlinks=True)
    copied_hash, copied_count = fingerprint_tree(root / "dependencies")
    if (source_hash, count) != (copied_hash, copied_count):
        raise ValueError("Dependency snapshot copy mismatch")
    protocol = {
        "version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "compiler_revision": revision,
        "compiler_source": str(source),
        "runner_sha256": sha(__file__),
        "python": sys.version,
        "node": subprocess.check_output(
            ["node", "--version"], env=env, text=True
        ).strip(),
        "configuration": safe_configuration(env),
        "frozen_files": frozen,
        "dependency_snapshot_sha256": source_hash,
        "dependency_entries": count,
        "blocks": blocks,
        "schedule": schedule(blocks),
        "arms": ARMS,
        "generation_timeout_seconds": generation_timeout,
        "protocol": "Serial fresh full pipelines in three predeclared randomized rotating blocks; no model-generating run overlaps. Same exact compiler/input/acceptance/environment/dependency snapshot; only event context and prefix flags differ. No failed attempt is repaired/replaced or excluded. Timeouts included as failures. All gates plus unchanged fixed14 and production14 required.",
        "speed_estimand": "Generation+final build wall seconds and complete-attempt wall seconds. Report ALL attempts, success-conditional summaries separately, failure-inclusive time and tokens per accepted application; never rank early failures as faster success. Block paired factorial effects with uncertainty; generation trajectory variance remains part of full pipeline behavior.",
        "cache_policy": "Provider best-effort caches cannot be reset or pinned; blocked interleaving reduces order bias, does not guarantee cold/warm matching. Count full pipeline SDK cache hit/miss by tokens, not average percentages. No automatic extra warm-up model calls.",
        "completion": "All declared attempts terminal, including failed ones; compute aggregate/ablation/uncertainty and cache diagnosis. No fixed threshold for reliability/speed is assumed. Three per arm provides exploratory evidence, not a high-confidence success-rate guarantee.",
    }
    save_json(root / "protocol.json", protocol)
    return protocol


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dependencies", type=Path, required=True)
    parser.add_argument("--env-source", type=Path, default=ROOT)
    parser.add_argument("--node-bin", type=Path, required=True)
    parser.add_argument("--blocks", type=int, default=3)
    parser.add_argument("--generation-timeout", type=int, default=1200)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    source, root = args.source.resolve(), args.output.resolve()
    env = environment(args.env_source.resolve(), args.node_bin.resolve())
    protocol = (
        read_summary(root / "protocol.json")
        if args.resume
        else initialize(
            source,
            root,
            args.dependencies.resolve(),
            env,
            args.blocks,
            args.generation_timeout,
        )
    )
    if protocol is None or protocol["runner_sha256"] != sha(__file__):
        parser.error(
            "Missing protocol or runner changed; cannot continue this campaign"
        )
    lock = root / "runner.lock"
    with lock.open("x") as stream:
        stream.write(str(os.getpid()))
    try:
        seal(source, protocol, env)
        results = []
        for item in protocol["schedule"]:
            path = root / "runs" / item["name"] / "result.json"
            if path.exists():
                results.append(read_summary(path))
                continue
            print(json.dumps({"event": "attempt_start", **item}), flush=True)
            record = run_one(source, root, protocol, item, env)
            results.append(record)
            save_json(root / "results.json", results)
            print(
                json.dumps(
                    {
                        "event": "attempt_end",
                        "name": item["name"],
                        "success": record["success"],
                        "wall_seconds": record["attempt_wall_seconds"],
                        "usage": record["usage"]["totals"],
                    }
                ),
                flush=True,
            )
        save_json(
            root / "complete.json",
            {
                "attempts": len(results),
                "successes": sum(row["success"] for row in results),
                "completed_utc": datetime.now(timezone.utc).isoformat(),
            },
        )
    finally:
        lock.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
