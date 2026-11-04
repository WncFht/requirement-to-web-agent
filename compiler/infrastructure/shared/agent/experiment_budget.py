"""Shared, fail-closed budget for serial stage experiments, including failed calls."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path


class ExperimentBudgetExceeded(RuntimeError):
    """No additional model request is allowed in this experiment."""


def limit_arguments(arguments):
    setting = os.getenv("ARC_EXPERIMENT_BUDGET")
    if not setting:
        return arguments
    record = json.loads(Path(setting).read_text())
    maximum = int(record.get("max_output_tokens", 12000))
    key = "max_tokens" if "max_tokens" in arguments else "max_completion_tokens"
    return {**arguments, key: min(int(arguments.get(key, maximum)), maximum)}


def reserve(arguments=None):
    """Reserve one SDK call before sending; pending/unknown usage blocks another call.

    The ledger is for one serial experiment process tree, not concurrent workers.
    Output limits and known returned usage do not constitute a billing cap.
    """
    setting = os.getenv("ARC_EXPERIMENT_BUDGET")
    if not setting:
        return None
    path = Path(setting)
    record = json.loads(path.read_text())
    now = datetime.now(timezone.utc)
    if record.get("closed"):
        raise ExperimentBudgetExceeded("Experiment is closed; keep its original results")
    if record.get("pending") or record.get("unknown_usage"):
        raise ExperimentBudgetExceeded("Pending or unknown model usage; stop this experiment")
    if now >= datetime.fromisoformat(record["deadline_utc"]):
        raise ExperimentBudgetExceeded("Experiment wall-clock budget exhausted")
    if record["calls"] >= record["max_calls"] or record["total_tokens"] >= record["max_tokens"]:
        raise ExperimentBudgetExceeded("Experiment call/token budget exhausted")
    if arguments:
        output = arguments.get("max_completion_tokens", arguments.get("max_tokens", 0))
        if record["total_tokens"] + record.get("last_prompt_tokens", 0) + output > record["max_tokens"]:
            raise ExperimentBudgetExceeded("Insufficient token headroom for prior prompt size plus requested output")
    record["calls"] += 1
    record["pending"] = True
    path.write_text(json.dumps(record, indent=2) + "\n")
    return path


def finish(path, usage):
    if path is None:
        return
    record = json.loads(path.read_text())
    record["pending"] = False
    total = (usage or {}).get("total_tokens")
    if not isinstance(total, int):
        record["unknown_usage"] = True
    else:
        record["total_tokens"] += total
        if isinstance((usage or {}).get("prompt_tokens"), int):
            record["last_prompt_tokens"] = usage["prompt_tokens"]
    path.write_text(json.dumps(record, indent=2) + "\n")
