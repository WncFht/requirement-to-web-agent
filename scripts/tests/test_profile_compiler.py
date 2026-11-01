"""Audited costs count SDK responses once and retain missing usage uncertainty."""

import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from profile_compiler import profile


class ProfileCompilerTests(unittest.TestCase):
    def test_http_mirrors_do_not_double_count_and_pending_usage_stays_unknown(self):
        rows = [
            {
                "event": "request",
                "call_id": "done",
                "activity": "design",
                "arguments": {},
            },
            {"event": "http_response", "call_id": "done"},
            {
                "event": "response",
                "call_id": "done",
                "stage": "Stage 02",
                "elapsed_seconds": 2,
                "response": {
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": 5,
                        "total_tokens": 15,
                    }
                },
            },
            {"event": "request", "call_id": "pending"},
        ]
        with TemporaryDirectory() as folder:
            path = Path(folder) / "calls.jsonl"
            path.write_text("\n".join(json.dumps(row) for row in rows))
            result = profile(path)
        self.assertEqual(result["totals"]["calls"], 1)
        self.assertEqual(result["totals"]["total_tokens"], 15)
        self.assertEqual(result["requests_without_returned_usage"], ["pending"])

    def test_cache_is_partitioned_by_real_edit_round_and_weighted_input(self):
        rows = []
        for call_id, activity, prompt, cached in (
            ("first", "Implementation | Edit round 1/18", 100, 0),
            ("repair", "Implementation | Edit round 3/18", 900, 810),
            ("other", "Design", 50, 10),
        ):
            rows.extend(
                [
                    {"event": "request", "call_id": call_id, "activity": activity},
                    {
                        "event": "response",
                        "call_id": call_id,
                        "stage": "Stage 12",
                        "response": {
                            "usage": {
                                "prompt_tokens": prompt,
                                "prompt_cache_hit_tokens": cached,
                                "total_tokens": prompt,
                            }
                        },
                    },
                ]
            )
        with TemporaryDirectory() as folder:
            path = Path(folder) / "calls.jsonl"
            path.write_text("\n".join(json.dumps(row) for row in rows))
            result = profile(path)
        groups = result["edit_round_groups"]
        self.assertEqual(groups["first_edit_round"]["uncached_input_tokens"], 100)
        later = groups["later_edit_round"]
        self.assertEqual(later["uncached_input_tokens"], 90)
        self.assertEqual(later["weighted_input_cache_hit_ratio"], 0.9)
        self.assertEqual(result["stage_edit_round_groups"]["Stage 12"], groups)
        self.assertEqual(
            sum(group["prompt_tokens"] for group in groups.values()),
            result["totals"]["prompt_tokens"],
        )
        self.assertEqual(sum(group["calls"] for group in groups.values()), 3)
