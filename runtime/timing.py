"""Append-only, nested wall-time spans; no commands, credentials or exception messages."""

from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from threading import RLock
from time import monotonic
from uuid import uuid4
import warnings

_active = ContextVar("compiler_timing_span", default=None)
_lock = RLock()


def child_environment():
    """Carry only opaque trace/parent identifiers into compiler-owned child processes."""
    current = _active.get()
    if not current:
        return {}
    return {
        "ARC_TIMING_TRACE_ID": current["trace_id"],
        "ARC_TIMING_PARENT_ID": current["span_id"],
    }


def _opaque(name):
    value = os.environ.get(name, "")
    return (
        value
        if len(value) == 32 and all(c in "0123456789abcdef" for c in value)
        else None
    )


def _write(output, value):
    # Telemetry failure must not change a gate's result or mask the original error.
    try:
        output.mkdir(parents=True, exist_ok=True)
        with (
            _lock,
            (output / "timings.jsonl").open(
                "a", encoding="utf-8", newline="\n"
            ) as stream,
        ):
            stream.write(json.dumps(value, ensure_ascii=False) + "\n")
    except OSError:
        try:
            warnings.warn(
                "Timing log unavailable; timing evidence is incomplete.",
                RuntimeWarning,
                stacklevel=2,
            )
        except Warning:
            pass


@contextmanager
def timed(kind, *, output=None, stage=None, name=None):
    """Record start/end even on failure; elapsed time includes nested children.

    The yielded dictionary accepts returncode/status only. No arbitrary payload,
    command arguments, environment values or exception text enter this log.
    Missing ends after a hard kill remain incomplete, never zero-duration work.
    """
    if os.getenv("ARC_DISABLE_TIMING", "0") == "1":
        yield {}
        return
    parent = _active.get()
    if output is None:
        if parent:
            output = parent["output"]
        else:
            from coding_agent.support.utils.presentation.logging import session_info

            session = session_info()
            if session:
                output, stage = session["output"], stage or session["stage"]
    if output is None:
        yield {}
        return
    context = {
        "output": Path(output),
        "trace_id": parent["trace_id"]
        if parent
        else _opaque("ARC_TIMING_TRACE_ID") or uuid4().hex,
        "span_id": uuid4().hex,
        "stage": stage or (parent["stage"] if parent else None),
    }
    base = {
        "version": 1,
        "trace_id": context["trace_id"],
        "span_id": context["span_id"],
        "parent_id": parent["span_id"] if parent else _opaque("ARC_TIMING_PARENT_ID"),
        "pid": os.getpid(),
        "kind": kind,
        "stage": context["stage"],
        "name": name,
    }
    token = _active.set(context)
    result = {}
    started = monotonic()
    _write(
        context["output"],
        {**base, "event": "start", "timestamp": datetime.now(timezone.utc).isoformat()},
    )
    error_type = None
    try:
        yield result
    except BaseException as error:
        error_type = type(error).__name__
        raise
    finally:
        duration = monotonic() - started
        code = result.get("returncode")
        status = (
            "error" if error_type else "nonzero" if code else result.get("status", "ok")
        )
        try:
            _write(
                context["output"],
                {
                    **base,
                    "event": "end",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "elapsed_seconds": duration,
                    "status": status,
                    "returncode": code,
                    "error_type": error_type,
                },
            )
        finally:
            _active.reset(token)


def command_kind(command):
    """Classify fixed compiler commands without copying their arguments into telemetry."""
    args = [str(part).replace("\\", "/") for part in command]
    if any(part.endswith("typescript/bin/tsc") for part in args):
        return "typecheck"
    if "--test" in args:
        return "backend_tests"
    if "frontend/scripts/test-e2e.mjs" in args:
        return "e2e_tests"
    if any(part.endswith("@playwright/test/cli.js") for part in args):
        return "browser_install" if "install" in args else "ui_tests"
    if "run" in args and "build" in args:
        return "build"
    if "run" in args and "db:init" in args:
        return "db_init"
    return "local_process"
