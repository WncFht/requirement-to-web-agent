"""Verify nested timing across real child processes without changing gate results."""

from contextlib import redirect_stdout
from io import StringIO
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import main
from infrastructure.utils.processes import capture_process, child_environment
from infrastructure.utils.timing import command_kind, timed
from infrastructure.utils.pipeline_state import identity
from infrastructure.utils.presentation.logging import console_log
from infrastructure.shared.models.text import TextModel
from infrastructure.utils.presentation.model_io import invoke
from types import SimpleNamespace
import httpx
from openai import APIConnectionError


class TimingTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = patch.dict(
            os.environ,
            {
                "ARC_DISABLE_TIMING": "0",
                "ARC_TIMING_TRACE_ID": "",
                "ARC_TIMING_PARENT_ID": "",
            },
        )
        self.env.start()
        self.addCleanup(self.env.stop)

    def rows(self):
        return [
            json.loads(line)
            for line in (self.root / "timings.jsonl").read_text().splitlines()
        ]

    def test_nested_span_and_monotonic_duration(self):
        with patch("infrastructure.utils.timing.monotonic", side_effect=[1, 2, 4, 7]):
            with timed("entrypoint", output=self.root):
                with timed("build", stage="finalize"):
                    pass
        outer, inner, inner_end, outer_end = self.rows()
        self.assertEqual(inner["parent_id"], outer["span_id"])
        self.assertEqual(inner["trace_id"], outer["trace_id"])
        self.assertEqual(inner_end["elapsed_seconds"], 2)
        self.assertEqual(outer_end["elapsed_seconds"], 6)

    def test_failures_nonzero_and_secrets_not_copied(self):
        with self.assertRaisesRegex(ValueError, "private-secret"):
            with timed("typecheck", output=self.root) as result:
                result["arbitrary"] = "private-secret"
                raise ValueError("private-secret")
        with timed("backend_tests", output=self.root) as result:
            result["returncode"] = 7
        rows = self.rows()
        self.assertEqual(rows[1]["error_type"], "ValueError")
        self.assertEqual(rows[3]["status"], "nonzero")
        self.assertEqual(rows[3]["returncode"], 7)
        self.assertNotIn("private-secret", json.dumps(rows))

    def test_capture_preserves_stdout_stderr_code_and_parent(self):
        with timed("stage_session", output=self.root):
            result = capture_process(
                [
                    sys.executable,
                    "-c",
                    "import sys;print('out');print('err',file=sys.stderr);sys.exit(3)",
                ],
                cwd=self.root,
                timeout=5,
            )
        self.assertEqual(
            result, {"returncode": 3, "stdout": "out\n", "output": "out\nerr\n"}
        )
        rows = self.rows()
        self.assertEqual(rows[2]["returncode"], 3)
        self.assertEqual(rows[1]["parent_id"], rows[0]["span_id"])

    def test_timeout_and_interrupt_record_original_error(self):
        with timed("stage_session", output=self.root):
            with self.assertRaises(subprocess.TimeoutExpired):
                capture_process(
                    [sys.executable, "-c", "import time;time.sleep(30)"],
                    cwd=self.root,
                    timeout=0.05,
                )
            with self.assertRaises(KeyboardInterrupt):
                with timed("model_request"):
                    raise KeyboardInterrupt()
        errors = [row["error_type"] for row in self.rows() if row["event"] == "end"]
        self.assertIn("TimeoutExpired", errors)
        self.assertIn("KeyboardInterrupt", errors)

    def test_real_subprocess_inherits_trace_and_parent_without_secrets(self):
        code = "from pathlib import Path;from infrastructure.utils.timing import timed;import sys\nwith timed('build',output=Path(sys.argv[1]),stage='child'): pass"
        with timed("pipeline_stage", output=self.root):
            capture_process(
                [sys.executable, "-c", code, str(self.root)], cwd=Path.cwd(), timeout=5
            )
        rows = self.rows()
        starts = {row["kind"]: row for row in rows if row["event"] == "start"}
        self.assertEqual(
            starts["build"]["trace_id"], starts["pipeline_stage"]["trace_id"]
        )
        self.assertEqual(
            starts["build"]["parent_id"], starts["local_process"]["span_id"]
        )
        self.assertNotEqual(starts["build"]["pid"], starts["pipeline_stage"]["pid"])

    def test_logging_session_binds_direct_stage_without_pipeline(self):
        with (
            redirect_stdout(StringIO()),
            patch.object(sys, "argv", ["10_implement_ui.py"]),
            console_log(self.root),
        ):
            with timed("typecheck"):
                pass
        starts = [row for row in self.rows() if row["event"] == "start"]
        self.assertEqual(starts[0]["kind"], "stage_session")
        self.assertIn("Stage 10", starts[1]["stage"])

    def test_disabled_timing_leaves_no_log_or_trace_and_same_result(self):
        with patch.dict(os.environ, {"ARC_DISABLE_TIMING": "1"}):
            with timed("pipeline", output=self.root):
                result = capture_process(
                    [sys.executable, "-c", "print('unchanged')"],
                    cwd=self.root,
                    timeout=5,
                )
                self.assertFalse(bool(child_environment().get("ARC_TIMING_TRACE_ID")))
        self.assertEqual(result["stdout"], "unchanged\n")
        self.assertFalse((self.root / "timings.jsonl").exists())

    def test_unwritable_telemetry_does_not_mask_business_result(self):
        (self.root / "timings.jsonl").mkdir()
        with patch("warnings.warn", side_effect=RuntimeWarning):
            with timed("build", output=self.root):
                pass
            with self.assertRaisesRegex(ValueError, "business"):
                with timed("build", output=self.root):
                    raise ValueError("business")

    def test_final_db_init_and_build_keep_commands_and_failures(self):
        with (
            timed("entrypoint", output=self.root),
            patch.object(main.subprocess, "run") as run,
        ):
            main.build_application(
                ["python", "run_all.py"], Path.cwd(), self.root, 3301
            )
        self.assertEqual(
            [call.args[0] for call in run.call_args_list],
            [
                ["python", "run_all.py"],
                ["npm", "run", "db:init"],
                ["npm", "run", "build"],
            ],
        )
        self.assertIn("3301", (self.root / "deploy.sh").read_text())
        self.assertEqual(
            [row["kind"] for row in self.rows() if row["event"] == "end"],
            ["db_init", "build", "entrypoint"],
        )
        with patch.object(
            main.subprocess,
            "run",
            side_effect=[None, subprocess.CalledProcessError(9, "db:init")],
        ):
            with self.assertRaises(subprocess.CalledProcessError):
                with timed("entrypoint", output=self.root):
                    main.build_application(
                        ["python", "run_all.py"], Path.cwd(), self.root, 3301
                    )

    def test_fixed_command_classification(self):
        for command, expected in [
            (["node", "node_modules/typescript/bin/tsc", "--noEmit"], "typecheck"),
            (["node", "--test", "test.ts"], "backend_tests"),
            (["node", "frontend/scripts/test-e2e.mjs"], "e2e_tests"),
            (
                ["node", "node_modules/@playwright/test/cli.js", "install", "chromium"],
                "browser_install",
            ),
            (["node", "node_modules/@playwright/test/cli.js", "test"], "ui_tests"),
            (["node", "npm-cli.js", "run", "build"], "build"),
            (["node", "npm-cli.js", "run", "db:init"], "db_init"),
        ]:
            self.assertEqual(command_kind(command), expected)

    def test_timing_flag_does_not_invalidate_resume_identity(self):
        source = Path.cwd()
        before = identity(source, source / "input")
        with patch.dict(
            os.environ, {"ARC_DISABLE_TIMING": "1", "ARC_TIMING_TRACE_ID": "a" * 32}
        ):
            self.assertEqual(before, identity(source, source / "input"))

    def test_sdk_span_has_same_call_id_as_raw_audit_and_keeps_response(self):
        response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content='{"ok":true}'))]
        )
        response.model_dump = lambda **kwargs: {
            "choices": [{"message": {"content": '{"ok":true}'}}]
        }
        client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=lambda **kwargs: response)
            )
        )
        with redirect_stdout(StringIO()), console_log(self.root):
            self.assertIs(
                invoke(client, {"model": "fixture", "messages": []}), response
            )
        audit = [
            json.loads(row)
            for row in (self.root / "model_calls.jsonl").read_text().splitlines()
        ]
        ends = [
            row
            for row in self.rows()
            if row["event"] == "end" and row["kind"] == "model_request"
        ]
        self.assertEqual(ends[0]["name"], audit[0]["call_id"])

    def test_outer_transport_retry_separates_backoff_and_preserves_attempts(self):
        model = TextModel.__new__(TextModel)
        model.name = "fixture"
        error = APIConnectionError(
            request=httpx.Request("POST", "https://fixture.invalid")
        )
        response = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content='{"ok":true}', refusal=None)
                )
            ]
        )
        with (
            patch.dict(os.environ, {"ARC_MODEL_TRANSPORT_RETRIES": "1"}),
            patch.object(model, "_request", side_effect=[error, response]) as request,
            patch("infrastructure.shared.models.text.time.sleep") as sleep,
            redirect_stdout(StringIO()),
            console_log(self.root),
        ):
            self.assertEqual(
                model.generate_json("Same prompt", {"original": True}), {"ok": True}
            )
        self.assertEqual(request.call_count, 2)
        sleep.assert_called_once_with(10)
        self.assertEqual(request.call_args_list[0], request.call_args_list[1])
        self.assertEqual(
            len(
                [
                    row
                    for row in self.rows()
                    if row["event"] == "end" and row["kind"] == "model_backoff"
                ]
            ),
            1,
        )
