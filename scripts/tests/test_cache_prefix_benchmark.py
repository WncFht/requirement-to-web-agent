"""Both benchmark arms must receive exactly the same task and settings."""

from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmark_cache_prefix import variants


class CachePrefixBenchmarkTests(unittest.TestCase):
    def test_variants_change_only_json_order_and_share_one_isolation_marker(self):
        payload = {
            "event_id": "EV-input",
            "event": {"read": ["text"]},
            "frontend_data": {"text": ""},
            "page_inventory": ["home"],
        }
        arguments = {
            "model": "fixture",
            "messages": [
                {"role": "system", "content": "Original policy"},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            "response_format": {"type": "json_object"},
            "max_completion_tokens": 1024,
        }
        before = deepcopy(arguments)
        control, candidate = variants(arguments, "same-experiment")
        self.assertEqual(arguments, before)
        self.assertEqual(control["messages"][0], candidate["messages"][0])
        self.assertIn("same-experiment", control["messages"][0]["content"])
        self.assertEqual(
            json.loads(control["messages"][-1]["content"]),
            json.loads(candidate["messages"][-1]["content"]),
        )
        self.assertEqual(
            control["messages"][-1]["content"], before["messages"][-1]["content"]
        )
        self.assertEqual(
            list(json.loads(candidate["messages"][-1]["content"]))[:2],
            ["frontend_data", "page_inventory"],
        )
        for key in ("model", "response_format", "max_completion_tokens"):
            self.assertEqual(control[key], candidate[key])
