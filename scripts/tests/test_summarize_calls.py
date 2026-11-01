"""Validate aggregation units, compression and incomplete evidence failures."""

import gzip
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from summarize_calls import successful_stage_times, summarize


class CallSummaryTests(unittest.TestCase):
    def test_stage_time_uses_last_success_and_excludes_failed_attempts(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "compiler.log"
            path.write_text(
                "[FAILED] Stage 09\nStopped after 400s\n"
                "[DONE] Stage 09\nCompleted in 5.0s\n"
                "[DONE] Stage 09\nCompleted in 2.0s\n"
                "[DONE] Stage 12\nCompleted in 3.0s\n"
            )
            self.assertEqual(successful_stage_times(path)["sum_seconds"], 5.0)

    def test_http_mirrors_do_not_duplicate_sdk_tokens(self):
        record = {
            "event": "response",
            "stage": "Stage 12",
            "elapsed_seconds": 1.5,
            "response": {
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 20,
                    "total_tokens": 120,
                    "prompt_cache_hit_tokens": 40,
                }
            },
        }
        content = "\n".join(
            json.dumps(value)
            for value in [{"event": "http_response"}, record, {"event": "error"}]
        )
        with TemporaryDirectory() as folder:
            path = Path(folder) / "calls.jsonl.gz"
            with gzip.open(path, "wt") as stream:
                stream.write(content)
            result = summarize(path)
        self.assertEqual(result["totals"]["total_tokens"], 120)
        self.assertEqual(result["totals"]["input_cache_hit_ratio"], 0.4)
        self.assertEqual(result["totals"]["model_seconds"], 1.5)
        self.assertEqual(result["events"]["error"], 1)

    def test_incomplete_usage_fails_instead_of_reporting_zero_cost(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "calls.jsonl"
            path.write_text(json.dumps({"event": "response", "response": {}}))
            with self.assertRaisesRegex(ValueError, "no usage"):
                summarize(path)

    def test_empty_log_has_no_cache_ratio(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "calls.jsonl"
            path.write_text("")
            self.assertIsNone(summarize(path)["totals"]["input_cache_hit_ratio"])
