"""Wait for the fixed factorial campaign, then validate the separately predeclared cache candidate."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from time import sleep

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from run_factorial_campaign import environment, safe_configuration, run_one, sha, git
from summarize_factorial_campaign import summarize
from infrastructure.utils.files import save_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--candidate-source", type=Path, required=True)
    parser.add_argument("--node-bin", type=Path, required=True)
    parser.add_argument("--source-log", type=Path, required=True)
    args = parser.parse_args()
    root = args.campaign.resolve()
    candidate = args.candidate_source.resolve()
    expected = json.loads((root / "cache-followup-protocol.json").read_text())
    while not (root / "complete.json").exists():
        # Never start model work while the registered serial compiler campaign is active.
        lock = root / "runner.lock"
        if not lock.exists():
            raise ValueError(
                "Primary runner stopped without completion; inspect existing handle/results, do not auto-restart"
            )
        pid = int(lock.read_text())
        if not Path("/proc", str(pid)).exists():
            raise ValueError(
                "Primary runner PID vanished without completion; follow-up remains unstarted"
            )
        sleep(10)
    analysis = summarize(root)
    if not analysis["complete"]:
        raise ValueError(
            "Primary completion marker does not cover all declared attempts"
        )
    if (root / "runner.lock").exists():
        # The marker precedes the runner finally block by a few instructions.
        sleep(1)
    if (root / "runner.lock").exists():
        raise ValueError(
            "Primary runner still owns its lock; no concurrent model work allowed"
        )
    save_json(root / "factorial-analysis.json", analysis)
    print(
        json.dumps(
            {
                "event": "factorial_complete",
                "arms": {
                    arm: {
                        key: value[key] for key in ("attempts", "successes", "failures")
                    }
                    for arm, value in analysis["arms"].items()
                },
            }
        ),
        flush=True,
    )
    if git(candidate, "rev-parse", "HEAD") != expected["candidate_revision"] or git(
        candidate, "status", "--porcelain"
    ):
        raise ValueError("Cache candidate differs from the registered source")
    env = environment(ROOT, args.node_bin.resolve())
    # The live replay precedes the full follow-ups and is excluded from their wall times.
    replay = root / "cache-refinement-live"
    with (root / "cache-refinement-live.log").open("w") as stream:
        subprocess.run(
            [
                sys.executable,
                str(candidate / "scripts/benchmark_cache_prefix.py"),
                str(args.source_log.resolve()),
                "--output",
                str(replay),
                "--pairs",
                str(expected["matched_pairs"]),
                "--refined-prefix",
            ],
            cwd=candidate,
            env=env,
            stdout=stream,
            stderr=stream,
            check=True,
        )
    print(json.dumps({"event": "cache_live_replay_complete"}), flush=True)
    follow = root / "cache-validation"
    follow.mkdir(exist_ok=False)
    # Same snapshot as the primary campaign, not a freshly resolved npm tree.
    (follow / "dependencies").symlink_to(
        root / "dependencies", target_is_directory=True
    )
    env["ARC_CACHE_PREFIX_V2"] = "1"
    protocol = {
        "version": 1,
        "compiler_revision": expected["candidate_revision"],
        "configuration": safe_configuration(env),
        "frozen_files": expected["frozen_files"],
        "generation_timeout_seconds": expected["generation_timeout_seconds"],
        "schedule": expected["full_attempts"],
        "purpose": "Two fixed-count V2 full generations after the completed V1 factorial campaign; no replacement on failure. Not added to the original factorial or repetition-rate denominator.",
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    save_json(follow / "protocol.json", protocol)
    results = []
    for item in protocol["schedule"]:
        print(json.dumps({"event": "cache_full_start", **item}), flush=True)
        result = run_one(candidate, follow, protocol, item, env)
        results.append(result)
        save_json(follow / "results.json", results)
        print(
            json.dumps(
                {
                    "event": "cache_full_end",
                    "name": item["name"],
                    "success": result["success"],
                    "usage": result["usage"]["totals"],
                }
            ),
            flush=True,
        )
    save_json(
        follow / "complete.json",
        {
            "attempts": len(results),
            "successes": sum(row["success"] for row in results),
            "completed_utc": datetime.now(timezone.utc).isoformat(),
        },
    )
    save_json(
        root / "all-experiments-complete.json",
        {
            "primary_attempts": analysis["terminal_attempts"],
            "cache_validation_attempts": len(results),
            "matched_pairs": expected["matched_pairs"],
        },
    )


if __name__ == "__main__":
    main()
