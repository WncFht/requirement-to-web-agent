"""Recompute trial outcomes from raw SDK responses, case results and immutable identities."""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from coding_agent.trace import audit as agent_audit, file_manifest, sha, usage_values
from scripts.run_factorial_campaign import fingerprint_tree, owned_output_processes


def load(path):
    return json.loads(Path(path).read_text())


def cases(raw):
    result = []

    def visit(node, parents=()):
        for spec in node.get("specs", []):
            for test in spec.get("tests", []):
                result.append(
                    {
                        "identity": [
                            spec.get("file"),
                            *parents,
                            spec["title"],
                            test.get("projectName"),
                        ],
                        "expected": test.get("expectedStatus", "passed"),
                        "status": test.get("status"),
                        "results": [r.get("status") for r in test.get("results", [])],
                    }
                )
        for child in node.get("suites", []):
            visit(child, parents + (child.get("title", ""),))

    visit(raw)
    return result


def oracle_green(raw, count):
    rows = cases(raw)
    identities = {json.dumps(r["identity"]) for r in rows}
    return (
        len(rows) == len(identities) == count
        and not raw.get("errors")
        and all(
            r["expected"] == "passed"
            and r["status"] == "expected"
            and r["results"] == ["passed"]
            for r in rows
        )
    )


def raw_usage(output, arm):
    rows, issues = [], []
    path = output / ("model_calls.jsonl" if arm == "A" else ".arc/agent/events.jsonl")
    if not path.exists():
        return {"total_tokens": 0, "responses": 0, "unknown": []}, ["Missing model log"]
    for line in path.read_text().splitlines():
        try:
            rows.append(json.loads(line))
        except ValueError:
            issues.append("Malformed model event")
    requests, responses, unknown, tokens = set(), set(), set(), 0
    for row in rows:
        event = row.get("event") if arm == "A" else row.get("kind")
        if event in {"request", "model.request"}:
            if row["call_id"] in requests:
                issues.append("Duplicate request")
            requests.add(row["call_id"])
        if event not in {"response", "model.response"}:
            continue
        call = row["call_id"]
        if call in responses:
            issues.append("Duplicate response")
            continue
        responses.add(call)
        response = (
            row["response"] if arm == "A" else load(output / row["artifact"]["path"])
        )
        try:
            tokens += usage_values(response.get("usage"))["total_tokens"]
        except ValueError:
            unknown.add(call)
    unknown |= requests - responses
    if responses - requests:
        issues.append("Response without request")
    return {
        "total_tokens": tokens,
        "responses": len(responses),
        "unknown": sorted(unknown),
    }, issues


def source_bytes(source, revision, relative):
    return subprocess.check_output(
        ["git", "show", revision + ":" + relative], cwd=source
    )


def audit(root, verify_dependencies=True):
    root = Path(root).resolve()
    protocol = load(root / "protocol.json")
    issues, missing, attempts = [], [], []
    source = Path(protocol["sources"]["B"]["path"])
    revision = protocol["sources"]["B"]["revision"]
    frozen = protocol["frozen_assertions"] | {
        "scripts/run_coding_campaign.py": protocol["runner_sha256"]
    }
    if protocol.get("notes_oracle_sha256"):
        frozen["experiments/notes-oracle/fixed.spec.ts"] = protocol[
            "notes_oracle_sha256"
        ]
    for relative, expected in frozen.items():
        if (
            hashlib.sha256(source_bytes(source, revision, relative)).hexdigest()
            != expected
        ):
            issues.append("Registered source identity differs: " + relative)
    if (
        protocol.get("input_path")
        and file_manifest(Path(protocol["input_path"])) != protocol["input_sha256"]
    ):
        issues.append("Input bytes changed")
    if verify_dependencies and protocol.get("dependency_path"):
        if (
            fingerprint_tree(Path(protocol["dependency_path"]))[0]
            != protocol["dependency_sha256"]
        ):
            issues.append("Dependency bytes changed")
    previous_end = None
    for item in protocol["schedule"]:
        directory = root / "runs" / item["name"]
        if not (directory / "result.json").exists():
            missing.append(item["name"])
            continue
        record, output = load(directory / "result.json"), directory / "output"
        found = []
        if (
            any(record.get(k) != v for k, v in item.items())
            or record["revision"] != protocol["sources"][item["arm"]]["revision"]
        ):
            found.append("Schedule/source mismatch")
        if record.get("protocol_sha256") and record["protocol_sha256"] != sha(
            root / "protocol.json"
        ):
            found.append("Protocol changed")
        begin, end = (
            datetime.fromisoformat(record[k]) for k in ("started_utc", "completed_utc")
        )
        if end < begin or previous_end is not None and begin < previous_end:
            found.append("Attempts overlap or timestamps reverse")
        previous_end = end
        usage, errors = raw_usage(output, item["arm"])
        found.extend(errors)
        if (
            usage["total_tokens"] != record["usage"]["totals"].get("total_tokens", 0)
            or usage["responses"] != record["usage"]["response_count"]
        ):
            found.append("Recorded usage differs from raw responses")
        if usage["unknown"] != record["usage"]["calls_with_unknown_usage"]:
            found.append("Unknown usage was hidden")
        if file_manifest(output, logs=True) != record["sealed_application"]:
            found.append("Application/evidence changed after trial")
        if not record.get("source_unchanged"):
            found.append("Missing source integrity proof")
        internal = False
        generation = record["phases"]["generation"]
        if generation["status"] == "finished" and generation["returncode"] == 0:
            if item["arm"] == "B":
                proof = agent_audit(output)
                internal = (
                    proof["valid"] and proof["result"]["status"] == "INTERNAL_GREEN"
                )
                found.extend(proof["issues"])
            else:
                internal = all(
                    load(output / ".arc" / (n + ".json")).get("status") == "GREEN"
                    for n in ("backend_tdd", "ui_checks", "frontend_e2e")
                )
        modes, leaf_cases = [], {}
        for mode in ("fixed", "production"):
            expected = record.get(mode)
            if not expected:
                modes.append(False)
                continue
            report = load(directory / mode / "playwright.json")
            leaf_cases[mode] = cases(report)
            actual = oracle_green(report, 5 if protocol["task"] == "notes" else 14)
            phase = record["phases"][mode]
            actual = (
                actual
                and phase["status"] == "finished"
                and phase["returncode"] == 0
                and expected["application_unchanged"]
            )
            if (
                report.get("stats") != expected["stats"]
                or (expected["status"] == "GREEN") != actual
            ):
                found.append("Oracle classification differs from raw cases: " + mode)
            if load(directory / mode / "summary.json") != expected:
                found.append("Oracle summary changed: " + mode)
            if (
                mode in record.get("sealed_evidence", {})
                and {
                    p.relative_to(directory / mode).as_posix(): sha(p)
                    for p in sorted((directory / mode).rglob("*"))
                    if p.is_file()
                }
                != record["sealed_evidence"][mode]
            ):
                found.append("Oracle original evidence changed: " + mode)
            modes.append(actual)
        success = internal and all(modes) and not usage["unknown"]
        if success != record["success"]:
            found.append("Full success classification lacks evidence")
        if owned_output_processes(output):
            found.append("Application processes remain")
        attempts.append(
            {
                "name": item["name"],
                "success": success,
                "valid": not found,
                "usage": usage,
                "cases": leaf_cases,
                "issues": found,
                "result_sha256": sha(directory / "result.json"),
            }
        )
        issues.extend(item["name"] + ": " + e for e in found)
    return {
        "complete": not missing,
        "valid_terminal_evidence": not issues,
        "missing_attempts": missing,
        "findings": issues,
        "attempts": attempts,
        "protocol_sha256": sha(root / "protocol.json"),
        "scope": "Recomputed returned SDK usage, unique actual Playwright cases, sealed bytes, source identities and serial timestamps. Unknown billing remains unknown.",
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("campaign", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        p.error("Use a new audit path")
    result = audit(args.campaign)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "attempts"}))
    sys.exit(0 if result["complete"] and result["valid_terminal_evidence"] else 1)
