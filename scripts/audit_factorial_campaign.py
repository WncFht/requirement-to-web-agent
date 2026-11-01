"""Verify a declared campaign against source/config identities, raw usage and real acceptance evidence."""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run_factorial_campaign import (
    ARMS,
    fingerprint_tree,
    git,
    model_usage,
    sha,
    success,
)


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def audit(root, verify_dependencies=True):
    protocol = load(root / "protocol.json")
    findings, evidence, missing = [], [], []
    source = Path(protocol["compiler_source"])
    if git(source, "rev-parse", "HEAD") != protocol["compiler_revision"] or git(
        source, "status", "--porcelain"
    ):
        findings.append("Frozen compiler checkout differs or is dirty")
    for relative, expected in protocol["frozen_files"].items():
        if sha(source / relative) != expected:
            findings.append("Changed frozen source: " + relative)
    if verify_dependencies:
        dependency_hash, count = fingerprint_tree(root / "dependencies")
        if (
            dependency_hash != protocol["dependency_snapshot_sha256"]
            or count != protocol["dependency_entries"]
        ):
            findings.append("Dependency snapshot changed")
    previous_end = None
    for item in protocol["schedule"]:
        output = root / "runs" / item["name"]
        path = output / "result.json"
        if not path.exists():
            missing.append(item["name"])
            continue
        record = load(path)
        issues = []
        if (
            any(
                record.get(key) != item[key]
                for key in ("name", "block", "position", "arm")
            )
            or record["compiler_revision"] != protocol["compiler_revision"]
        ):
            issues.append("Source/schedule mismatch")
        expected = protocol["configuration"] | {
            "ARC_EVENT_CONTEXT": str(ARMS[item["arm"]][0]),
            "ARC_CACHE_PREFIX": str(ARMS[item["arm"]][1]),
        }
        if record["configuration"] != expected:
            issues.append("Configuration differs beyond declared two flags")
        if record["post_run_source_integrity"] != "PASSED":
            issues.append("Missing post-run integrity validation")
        begin = datetime.fromisoformat(record["started_utc"])
        end = datetime.fromisoformat(record["completed_utc"])
        if end < begin or previous_end is not None and begin < previous_end:
            issues.append("Attempt timestamps overlap or reverse")
        previous_end = end
        recomputed = model_usage(output / "model_calls.jsonl")
        if recomputed != record["usage"]:
            issues.append("Recorded token counts/hash differ from raw SDK audit")
        for name in ("backend_tdd", "ui_checks", "frontend_e2e"):
            gate = output / ".arc" / (name + ".json")
            actual = load(gate) if gate.exists() else None
            if actual != record["gates"][name]:
                issues.append("Gate report changed: " + name)
        copied_tests = output / "frontend/tests/fixed-campaign"
        if record.get("fixed") is not None and not copied_tests.is_dir():
            issues.append(
                "Copied immutable teacher/fixed assertion directory is missing"
            )
        if copied_tests.exists():
            for relative, expected_hash in protocol["frozen_files"].items():
                if relative.startswith("input/tests/"):
                    copy = copied_tests / "teacher" / Path(relative).name
                elif relative.startswith("acceptance/") and relative.endswith(".ts"):
                    copy = copied_tests / Path(relative).name
                else:
                    continue
                if not copy.exists() or sha(copy) != expected_hash:
                    issues.append(
                        "Copied teacher/fixed assertions changed: " + relative
                    )
        if success(record) != record["success"]:
            issues.append("Success classification not supported by gates and phases")
        for folder, key in (
            ("teacher-acceptance", "fixed"),
            ("production-acceptance", "production"),
        ):
            summary = output / ".arc" / folder / "campaign/summary.json"
            actual = load(summary) if summary.exists() else None
            if actual != record[key]:
                issues.append("Acceptance summary changed: " + folder)
            if record[key]:
                raw = load(output / ".arc" / folder / "campaign/playwright.json")
                if raw.get("stats") != actual.get("stats"):
                    issues.append(
                        "Acceptance stats differ from raw Playwright: " + folder
                    )
                if actual.get("status") == "GREEN" and raw.get("errors"):
                    issues.append("Successful acceptance has runner errors: " + folder)
        timing = output / "timings.jsonl"
        if timing.exists():
            starts, ends = set(), set()
            for line in timing.read_text().splitlines():
                value = json.loads(line)
                (starts if value["event"] == "start" else ends).add(value["span_id"])
            unclosed = sorted(starts - ends)
        else:
            unclosed = []
        evidence.append(
            {
                "name": item["name"],
                "valid": not issues,
                "issues": issues,
                "result_sha256": sha(path),
                "model_log_sha256": recomputed["log_sha256"],
                "timing_log_sha256": sha(timing) if timing.exists() else None,
                "unclosed_timing_spans": unclosed,
                "success": record["success"],
            }
        )
        findings.extend(item["name"] + ": " + issue for issue in issues)
    return {
        "complete": not missing,
        "valid_terminal_evidence": not findings,
        "missing_attempts": missing,
        "protocol_sha256": sha(root / "protocol.json"),
        "compiler_revision": protocol["compiler_revision"],
        "findings": findings,
        "attempts": evidence,
        "scope": "Raw SDK response usage/hash, exact source/input/assertion bytes, configurations, schedule and serial timestamp order, gate and acceptance summaries against raw Playwright stats. Unclosed spans retained as unknown. Does not certify provider routing, billing or external host isolation.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Refusing to overwrite an evidence audit")
    result = audit(args.campaign.resolve())
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    if result["findings"]:
        parser.exit(1, "Campaign audit failed; inspect findings.\n")


if __name__ == "__main__":
    main()
