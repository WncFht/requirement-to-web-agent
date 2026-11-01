"""Preserve failed assertions while removing proven duplicate report text."""

import copy
import json
import os
import unittest
from unittest.mock import patch

from infrastructure.shared.agent.loop import (
    CheckFailure,
    compact_feedback,
    repair_feedback,
)
from infrastructure.stages.frontend.ui.testing import require_green


class FeedbackTests(unittest.TestCase):
    def report(self):
        fields = {
            "returncode": 1,
            "passed": 6,
            "failed": 1,
            "errors": [],
            "failures": ["\x1b[31mExpected username\x1b[0m\nreq2.spec.ts:75"],
        }
        return fields | {"output": json.dumps(fields)}

    @patch.dict(os.environ, {"ARC_FULL_FEEDBACK": "0"})
    def test_readable_failure_preserves_counts_and_assertion_location(self):
        report = self.report()
        original = copy.deepcopy(report)
        with self.assertRaises(CheckFailure) as caught:
            require_green(report)
        value = repair_feedback(caught.exception)
        self.assertEqual(value["checks"]["failed"], 1)
        self.assertEqual(
            value["checks"]["failures"], ["Expected username\nreq2.spec.ts:75"]
        )
        self.assertNotIn("output", value["checks"])
        self.assertEqual(report, original)

    def test_distinct_or_truncated_output_is_retained(self):
        report = self.report() | {"output": "server startup failed"}
        self.assertEqual(compact_feedback(report)["output"], "server startup failed")
        report["output"] = json.dumps({"failed": 1})
        self.assertIn("output", compact_feedback(report))

    @patch.dict(os.environ, {"ARC_FULL_FEEDBACK": "1"})
    def test_opt_out_restores_legacy_exception_feedback(self):
        error = CheckFailure("UI checks are not GREEN", self.report())
        self.assertEqual(repair_feedback(error), {"error": str(error)})
        self.assertIn("output", compact_feedback(self.report()))

    def test_gate_still_rejects_failed_and_empty_suites(self):
        for report in [self.report(), {"returncode": 0, "passed": 0}]:
            with self.assertRaises(ValueError):
                require_green(report)
        self.assertIsNone(require_green({"returncode": 0, "passed": 1}))

    def test_ordinary_errors_keep_existing_repair_format(self):
        self.assertEqual(repair_feedback(ValueError("bad path")), {"error": "bad path"})
