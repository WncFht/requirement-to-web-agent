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
