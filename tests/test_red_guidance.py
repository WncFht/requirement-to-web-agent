"""Improve actionable feedback without admitting action timeouts as behavioral RED."""

import os
import unittest
from unittest.mock import patch

from infrastructure.shared.agent.loop import CheckFailure, repair_feedback
from infrastructure.stages.frontend.interactions.testing import require_behavioral_red


class RedGuidanceTests(unittest.TestCase):
    def report(self, failure):
        return {
            "returncode": 1,
            "passed": 0,
            "failed": 1,
            "errors": [],
            "skipped": 0,
            "flaky": 0,
            "failures": [failure],
            "output": "full diagnostic",
        }

    def test_action_timeout_is_still_rejected_with_specific_ordering_guidance(self):
        report = self.report(
            "Test timeout of 30000ms exceeded.\nError: locator.click: Test timeout of 30000ms exceeded.\nwaiting for button"
        )
        with patch.dict(os.environ, {"ARC_FULL_FEEDBACK": "0"}):
            with self.assertRaises(CheckFailure) as raised:
                require_behavioral_red(report)
            self.assertIs(raised.exception.report, report)
            feedback = repair_feedback(raised.exception)
        self.assertIn("Before EVERY", feedback["error"])
        self.assertIn("toBeVisible", feedback["error"])
        self.assertEqual(feedback["checks"], report)

    def test_original_assertion_red_is_accepted_and_runtime_failure_is_not(self):
        require_behavioral_red(
            self.report("Error: expect(locator).toBeVisible() failed")
        )
        with self.assertRaises(CheckFailure):
            require_behavioral_red(self.report("ReferenceError: missing runtime"))
