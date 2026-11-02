"""Offline regressions for real failure boundaries of the coding-agent tools."""

import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from coding_agent.config import Config
from coding_agent.protocol import parse_action, green
from coding_agent.trace import Trace, audit, usage_values, sha
from coding_agent.workspace import Workspace


class CodingCoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.inputs, self.output = self.root / "input", self.root / "output"
        self.inputs.mkdir()
        self.output.mkdir()
        (self.inputs / "requirements.yaml").write_text("id: ROOT\n")
        self.workspace = Workspace(self.output, self.inputs)

    def test_platform_injected_credentials_and_default_model(self):
        with patch.dict(
            os.environ,
            {
                "OPENAI_BASE_URL": "http://localhost/v1",
                "OPENAI_API_KEY": "local-fixture",
            },
            clear=True,
        ):
            config = Config.environment(self.inputs, self.output)
        self.assertEqual(config.model, "deepseek-flash")
        self.assertNotIn("local-fixture", repr(config))
        self.assertNotIn("api_key", config.public())
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "injected"):
                Config.environment(self.inputs, self.output)

    def test_strict_json_keeps_premature_root_closure_as_error(self):
        with self.assertRaises(json.JSONDecodeError):
            parse_action('{"action":"read","paths":["x"]},"discarded":1}')
        with self.assertRaises(ValueError):
            parse_action('{"action":"edit","edits":[]}')
        self.assertEqual(
            parse_action('{"action":"finish"}\n</result>'), {"action": "finish"}
        )
        with self.assertRaises(json.JSONDecodeError):
            parse_action('{"action":"finish"},"discarded":1}</result>')

    def test_case_traversal_symlink_and_test_permissions(self):
        for name in (
            "../escape.ts",
            "/absolute",
            "backend/src/../../escape",
            ".env",
            "frontend/node_modules/a",
        ):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.workspace.path(name)
        (self.output / "frontend").mkdir()
        (self.output / "frontend/src").symlink_to(self.inputs, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Symlink"):
            self.workspace.path("frontend/src/file.ts")
        self.assertFalse(self.workspace.writable("backend/tests/support/context.ts"))
        self.workspace.frozen = True
        self.assertFalse(
            self.workspace.writable("frontend/tests/e2e/workflows.spec.ts")
        )
        self.assertTrue(self.workspace.writable("backend/src/api/register.ts"))
        self.assertTrue(self.workspace.writable("frontend/src/App.tsx"))

    def test_existing_files_require_fresh_hash_and_unique_exact_match(self):
        self.workspace.frozen = True
        self.workspace.apply([{"path": "frontend/src/a.ts", "content": "same\nsame\n"}])
        path = self.output / "frontend/src/a.ts"
        before = path.read_bytes()
        with self.assertRaisesRegex(ValueError, "Stale"):
            self.workspace.apply(
                [
                    {
                        "path": "frontend/src/a.ts",
                        "expected_sha256": "bad",
                        "old_text": "same",
                        "new_text": "new",
                    }
                ]
            )
        with self.assertRaisesRegex(ValueError, "exactly once"):
            self.workspace.apply(
                [
                    {
                        "path": "frontend/src/a.ts",
                        "expected_sha256": sha(path),
                        "old_text": "same",
                        "new_text": "new",
                    }
                ]
            )
        self.assertEqual(path.read_bytes(), before)

    def test_partial_second_write_restores_the_entire_batch(self):
        self.workspace.frozen = True
        self.workspace.apply(
            [{"path": f"frontend/src/{n}.ts", "content": n} for n in ("a", "b")]
        )
        edits = [
            {
                "path": f"frontend/src/{n}.ts",
                "expected_sha256": sha(self.output / f"frontend/src/{n}.ts"),
                "old_text": n,
                "new_text": "new",
            }
            for n in ("a", "b")
        ]
        original = Path.write_text

        def fail_second(path, text, *args, **kwargs):
            if path.name == "b.ts":
                path.write_bytes(b"partial")
                raise OSError("simulated disk failure")
            return original(path, text, *args, **kwargs)

        with patch.object(Path, "write_text", fail_second), self.assertRaises(OSError):
            self.workspace.apply(edits)
        self.assertEqual((self.output / "frontend/src/a.ts").read_text(), "a")
        self.assertEqual((self.output / "frontend/src/b.ts").read_text(), "b")

    def test_empty_skipped_todo_flaky_expected_failure_never_green(self):
        self.assertTrue(green({"returncode": 0, "passed": 2}))
        for row in (
            {"returncode": 0, "passed": 0},
            *(
                {"returncode": 0, "passed": 2, key: 1}
                for key in ("skipped", "todo", "flaky", "expected_failures", "failed")
            ),
        ):
            with self.subTest(row=row):
                self.assertFalse(green(row))

    def test_usage_missing_fields_are_unknown_not_zero(self):
        for value in (
            None,
            {},
            {"total_tokens": 4},
            {"prompt_tokens": 2, "completion_tokens": 3, "total_tokens": 4},
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                usage_values(value)

    def test_audit_checks_raw_usage_duplicates_and_changed_application(self):
        trace = Trace(self.output)
        path = self.output / "app.ts"
        path.write_text("original")
        trace.emit("model.request", call_id="one")
        trace.response(
            "one",
            {
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 3,
                    "total_tokens": 13,
                }
            },
        )
        trace.seal("FAILED_CHECK")
        self.assertTrue(audit(self.output)["valid"])
        path.write_text("changed after checks")
        self.assertFalse(audit(self.output)["valid"])

    def test_unfinished_call_is_not_complete_cost_evidence(self):
        trace = Trace(self.output)
        trace.emit("model.request", call_id="unfinished")
        trace.seal("INTERRUPTED")
        self.assertFalse(audit(self.output)["valid"])


if __name__ == "__main__":
    unittest.main()
