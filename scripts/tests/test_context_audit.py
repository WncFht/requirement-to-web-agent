"""Context reports preserve identities and sizes without copying source contents."""

import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from context_audit import audit


class ContextAuditTests(unittest.TestCase):
    def test_source_text_is_not_emitted_and_repeated_content_is_counted(self):
        payload = {
            "task": {"requirement": {}},
            "files": {
                "a.ts": {"content": "PRIVATE_SOURCE", "writable": True},
                "b.ts": {"content": "PRIVATE_SOURCE", "writable": False},
            },
            "feedback": [],
        }
        record = {
            "event": "request",
            "call_id": "fixture",
            "stage": "Stage 10",
            "arguments": {
                "messages": [
                    {"role": "system", "content": "instructions"},
                    {"role": "user", "content": json.dumps(payload)},
                ]
            },
        }
        with TemporaryDirectory() as folder:
            path = Path(folder) / "calls.jsonl"
            path.write_text(json.dumps(record) + "\n")
            result = audit(path)
        self.assertNotIn("PRIVATE_SOURCE", json.dumps(result))
        self.assertEqual(result["calls"][0]["duplicate_file_content_groups"], 1)
        self.assertEqual(result["calls"][0]["files"][0]["characters"], 14)
