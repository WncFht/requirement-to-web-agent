"""The actual new model client must bound retries and retain unknown or truncated usage."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import httpx
from openai import APITimeoutError, RateLimitError

from coding_agent.config import Config
from coding_agent.model import Model
from coding_agent.trace import Trace


class CodingModelTests(unittest.TestCase):
    def fixture(self, root, response_usage=True, finish="stop"):
        config = Config(
            Path(root) / "input",
            Path(root) / "output",
            base_url="http://unused.invalid/v1",
            api_key="local-fixture",
        )
        trace = Trace(config.output)
        raw = {
            "choices": [
                {"finish_reason": finish, "message": {"content": '{"action":"finish"}'}}
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 3, "total_tokens": 13}
            if response_usage
            else None,
        }
        response = SimpleNamespace(
            model_dump=lambda **kw: raw,
            choices=[
                SimpleNamespace(
                    finish_reason=finish,
                    message=SimpleNamespace(
                        content='{"action":"finish"}', refusal=None
                    ),
                )
            ],
        )
        client = Mock()
        client.with_options.return_value = client
        client.chat.completions.create.return_value = response
        with patch("coding_agent.model.OpenAI", return_value=client):
            model = Model(config, trace)
        return model, trace, client, response

    def test_rate_limit_has_one_retry_and_only_the_returned_response_is_counted(self):
        with TemporaryDirectory() as root:
            model, trace, client, response = self.fixture(root)
            request = httpx.Request("POST", "http://unused.invalid/v1/chat/completions")
            error = RateLimitError(
                "fixture", response=httpx.Response(429, request=request), body=None
            )
            client.chat.completions.create.side_effect = [error, response]
            with patch("coding_agent.model.time.sleep") as sleep:
                action, _ = model.generate([], 30)
            self.assertEqual(action, {"action": "finish"})
            self.assertEqual(client.chat.completions.create.call_count, 2)
            sleep.assert_called_once()
            self.assertEqual(trace.tokens, 13)
            self.assertFalse(trace.evidence_complete)
            events = [
                json.loads(line)
                for line in (trace.root / "events.jsonl").read_text().splitlines()
            ]
            self.assertEqual(sum(e["kind"] == "model.request" for e in events), 2)
            self.assertEqual(sum(e["kind"] == "model.response" for e in events), 1)

    def test_timeout_with_insufficient_remaining_budget_does_not_retry(self):
        with TemporaryDirectory() as root:
            model, _, client, _ = self.fixture(root)
            client.chat.completions.create.side_effect = APITimeoutError(
                request=httpx.Request("POST", "http://unused.invalid")
            )
            with self.assertRaisesRegex(RuntimeError, "TRANSPORT_FAILED"):
                model.generate([], 2)
            self.assertEqual(client.chat.completions.create.call_count, 1)

    def test_missing_usage_stops_and_truncation_still_counts_actual_tokens(self):
        with TemporaryDirectory() as root:
            model, trace, client, _ = self.fixture(root, response_usage=False)
            with self.assertRaisesRegex(RuntimeError, "Unknown model usage"):
                model.generate([], 30)
            self.assertEqual(client.chat.completions.create.call_count, 1)
            self.assertFalse(trace.evidence_complete)
        with TemporaryDirectory() as root:
            model, trace, _, _ = self.fixture(root, finish="length")
            with self.assertRaisesRegex(ValueError, "Output truncated"):
                model.generate([], 30)
            self.assertEqual(trace.tokens, 13)
