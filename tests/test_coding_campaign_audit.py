"""Independent audit rejects superficially green reports and understated model cost."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.audit_coding_campaign import oracle_green, raw_usage


class CodingCampaignAuditTests(unittest.TestCase):
    def reporter(self):
        return {
            "errors": [],
            "stats": {"expected": 1},
            "suites": [
                {
                    "title": "suite",
                    "specs": [
                        {
                            "file": "fixed.spec.ts",
                            "title": "persists",
                            "tests": [
                                {
                                    "expectedStatus": "passed",
                                    "status": "expected",
                                    "results": [{"status": "passed"}],
                                }
                            ],
                        }
                    ],
                }
            ],
        }

    def test_raw_cases_override_green_summary_and_reject_duplicates(self):
        raw = self.reporter()
        self.assertTrue(oracle_green(raw, 1))
        test = raw["suites"][0]["specs"][0]["tests"][0]
        test["results"][0]["status"] = "skipped"
        self.assertFalse(oracle_green(raw, 1))
        test["results"][0]["status"] = "passed"
        raw["suites"][0]["specs"].append(raw["suites"][0]["specs"][0])
        self.assertFalse(oracle_green(raw, 2))

    def test_missing_usage_and_duplicate_response_are_not_zero_cost_success(self):
        with TemporaryDirectory() as tmp:
            output = Path(tmp)
            rows = [
                {"event": "request", "call_id": "one"},
                {"event": "response", "call_id": "one", "response": {"usage": None}},
            ]
            path = output / "model_calls.jsonl"
            path.write_text("\n".join(map(json.dumps, rows)))
            usage, issues = raw_usage(output, "A")
            self.assertEqual(usage["unknown"], ["one"])
            self.assertEqual(issues, [])
            rows[1]["response"]["usage"] = {
                "prompt_tokens": 12,
                "completion_tokens": 3,
                "total_tokens": 15,
            }
            rows.append(rows[1])
            path.write_text("\n".join(map(json.dumps, rows)))
            usage, issues = raw_usage(output, "A")
            self.assertEqual(usage["total_tokens"], 15)
            self.assertIn("Duplicate response", issues)
