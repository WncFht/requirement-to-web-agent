"""Evidence audit must reject later changes to token records and claimed acceptance."""

import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from audit_factorial_campaign import audit
from run_factorial_campaign import model_usage


class FactorialAuditTests(unittest.TestCase):
    def fixture(self, root):
        source = root / "source"
        source.mkdir()
        protocol = {
            "compiler_source": str(source),
            "compiler_revision": "same",
            "frozen_files": {},
            "configuration": {},
            "schedule": [{"name": "one", "block": 1, "position": 1, "arm": "11"}],
        }
        (root / "protocol.json").write_text(json.dumps(protocol))
        output = root / "runs/one"
        output.mkdir(parents=True)
        (output / "model_calls.jsonl").write_text("")
        record = {
            "name": "one",
            "block": 1,
            "position": 1,
            "arm": "11",
            "compiler_revision": "same",
            "configuration": {"ARC_EVENT_CONTEXT": "1", "ARC_CACHE_PREFIX": "1"},
            "post_run_source_integrity": "PASSED",
            "started_utc": "2026-11-02T00:00:00+00:00",
            "completed_utc": "2026-11-02T00:00:01+00:00",
            "usage": model_usage(output / "model_calls.jsonl"),
            "gates": {"backend_tdd": None, "ui_checks": None, "frontend_e2e": None},
            "phases": {"generation": {"status": "finished", "returncode": 1}},
            "fixed": None,
            "production": None,
            "success": False,
        }
        (output / "result.json").write_text(json.dumps(record))
        return output, record

    def test_failed_attempt_can_have_valid_evidence_without_being_called_success(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            with patch(
                "audit_factorial_campaign.git",
                side_effect=lambda source, *args: (
                    "same" if args[0] == "rev-parse" else ""
                ),
            ):
                result = audit(root, verify_dependencies=False)
        self.assertTrue(result["complete"])
        self.assertTrue(result["valid_terminal_evidence"])
        self.assertFalse(result["attempts"][0]["success"])

    def test_altered_usage_success_and_configuration_are_detected(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            output, record = self.fixture(root)
            record["usage"]["totals"]["total_tokens"] = 0
            record["success"] = True
            record["configuration"]["ARC_CACHE_PREFIX"] = "0"
            (output / "result.json").write_text(json.dumps(record))
            with patch(
                "audit_factorial_campaign.git",
                side_effect=lambda source, *args: (
                    "same" if args[0] == "rev-parse" else ""
                ),
            ):
                result = audit(root, verify_dependencies=False)
        self.assertFalse(result["valid_terminal_evidence"])
        self.assertTrue(any("SDK audit" in issue for issue in result["findings"]))
        self.assertTrue(any("Configuration" in issue for issue in result["findings"]))
        self.assertTrue(
            any("Success classification" in issue for issue in result["findings"])
        )

    def test_missing_attempt_remains_incomplete_instead_of_disappearing(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            output, _ = self.fixture(root)
            (output / "result.json").unlink()
            with patch(
                "audit_factorial_campaign.git",
                side_effect=lambda source, *args: (
                    "same" if args[0] == "rev-parse" else ""
                ),
            ):
                result = audit(root, verify_dependencies=False)
        self.assertFalse(result["complete"])
        self.assertEqual(result["missing_attempts"], ["one"])
