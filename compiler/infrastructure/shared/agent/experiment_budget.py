"""Shared, fail-closed budget for serial stage experiments, including failed calls."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path


class ExperimentBudgetExceeded(RuntimeError):
    """No additional model request is allowed in this experiment."""


def reserve():
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
    if record.get("pending") or record.get("unknown_usage"):
        raise ExperimentBudgetExceeded("Pending or unknown model usage; stop this experiment")
    if now >= datetime.fromisoformat(record["deadline_utc"]):
        raise ExperimentBudgetExceeded("Experiment wall-clock budget exhausted")
    if record["calls"] >= record["max_calls"] or record["total_tokens"] >= record["max_tokens"]:
        raise ExperimentBudgetExceeded("Experiment call/token budget exhausted")
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
    path.write_text(json.dumps(record, indent=2) + "\n")
