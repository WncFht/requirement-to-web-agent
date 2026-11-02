"""Architecture comparisons must retain failed costs and missing-cost uncertainty."""

import unittest
from scripts.summarize_coding_campaign import arm_summary


class CodingMetricsTests(unittest.TestCase):
    def test_failed_attempts_are_charged_to_each_success(self):
        rows = [
            {
                "success": success,
                "tokens": tokens,
                "wall_seconds": 10,
                "unknown_usage": [],
                "reason": "fixture",
            }
            for success, tokens in ((False, 900), (True, 100))
        ]
        result = arm_summary(rows)
        self.assertEqual(result["tokens_per_success"], 1000)
        self.assertEqual(result["failed_known_tokens"], 900)
        self.assertEqual(result["seconds_per_success"], 20)
        rows[1]["success"] = False
        self.assertIsNone(arm_summary(rows)["tokens_per_success"])
        rows[1]["success"] = True
        rows[0]["unknown_usage"] = ["unreturned-request"]
        self.assertIsNone(arm_summary(rows)["tokens_per_success"])
