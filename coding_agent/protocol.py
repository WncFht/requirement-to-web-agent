"""Small JSON action protocol, shared observations, and strict check predicates."""

import json


class BudgetExhausted(RuntimeError):
    """The shared wall-time, call or token allowance has ended."""


class InvalidTest(ValueError):
    """A test contradicts its setup or violates the frozen-test boundary."""


def parse_action(content):
    value = json.loads(content)
    if not isinstance(value, dict) or value.get("action") not in {
        "read",
        "search",
        "edit",
        "check",
        "finish",
    }:
        raise ValueError(
            "Return one JSON object with action=read/search/edit/check/finish"
        )
    kind = value["action"]
    required = {
        "read": {"paths": list},
        "search": {"query": str},
        "edit": {"edits": list},
        "check": {"name": str},
        "finish": {},
    }[kind]
    for key, dtype in required.items():
        if key not in value or not isinstance(value[key], dtype):
            raise ValueError(f"Invalid action field: {kind}.{key}")
    if kind == "read" and (
        not value["paths"] or any(not isinstance(p, str) for p in value["paths"])
    ):
        raise ValueError("read.paths must be a nonempty list of paths")
    if kind == "edit" and not value["edits"]:
        raise ValueError("edit.edits must not be empty")
    return value


def observation(status, summary, **data):
    return {"status": status, "summary": summary, **data}


def green(report):
    return (
        report.get("returncode") == 0
        and report.get("passed", 0) > 0
        and not any(
            report.get(key)
            for key in (
                "failed",
                "skipped",
                "todo",
                "flaky",
                "expected_failures",
                "errors",
            )
        )
    )
