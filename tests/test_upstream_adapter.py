"""The platform wrapper delegates to upstream and never accepts its failed report."""

import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

import main


class UpstreamAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.inputs, self.output = self.root / "input", self.root / "output"
        self.inputs.mkdir()
        self.output.mkdir()
        (self.inputs / "requirements.yaml").write_text("id: ROOT\nchildren: []\n")

    def report(self, status):
        (self.output / ".arc").mkdir(exist_ok=True)
        (self.output / ".arc/compilation.json").write_text(
            json.dumps({"status": status})
        )
        for name in ("backend", "frontend"):
            (self.output / name).mkdir(exist_ok=True)
        for name in ("package.json", "deploy.sh"):
            (self.output / name).write_text("fixture")

    def test_upstream_command_port_and_environment_do_not_modify_reasoning(self):
        self.report("GREEN")
        with (
            patch.dict(
                os.environ,
                {
                    "OPENAI_BASE_URL": "http://127.0.0.1:1/v1",
                    "OPENAI_API_KEY": "fixture",
                    "MODEL_REASONING": "high",
                },
                clear=True,
            ),
            patch.object(
                main, "start_process", return_value=Mock(wait=Mock(return_value=0))
            ) as start,
        ):
            main.generate_application(
                self.root, self.inputs, self.output, 33000, "upstream", True
            )
        self.assertEqual(
            start.call_args.args[0],
            [
                main.sys.executable,
                str(self.root / "upstream/main.py"),
                str(self.inputs),
                "--output-dir",
                str(self.output),
                "--port",
                "33000",
                "--model-log",
            ],
        )
        env = start.call_args.kwargs["env"]
        self.assertEqual(env["MODEL"], "deepseek-flash")
        self.assertEqual(env["MODEL_REASONING"], "high")
        self.assertNotIn("ARC_DISABLE_THINKING", env)
        self.assertEqual(env["OPENAI_API_KEY"], "fixture")

    def test_zero_exit_does_not_turn_failed_or_missing_report_green(self):
        for status in (None, "FAILED", "COMPLETED_WITH_FAILURES"):
            with self.subTest(status=status):
                if status:
                    self.report(status)
                with patch.object(
                    main, "start_process", return_value=Mock(wait=Mock(return_value=0))
                ):
                    with self.assertRaisesRegex(RuntimeError, "not GREEN"):
                        main.generate_application(
                            self.root, self.inputs, self.output, 3000, "upstream"
                        )

    def test_interrupt_cleans_only_the_owned_upstream_process(self):
        process = Mock(wait=Mock(side_effect=KeyboardInterrupt()))
        with (
            patch.object(main, "start_process", return_value=process),
            patch.object(main, "stop_process") as stop,
        ):
            with self.assertRaises(KeyboardInterrupt):
                main.generate_application(
                    self.root, self.inputs, self.output, 3000, "upstream"
                )
        stop.assert_called_once_with(process)

    def test_default_main_selects_upstream_and_old_engine_is_not_an_alias(self):
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(main, "generate_application") as generate,
        ):
            main.main([str(self.inputs), "--output-dir", str(self.output)])
        self.assertEqual(generate.call_args.args[4], "upstream")
        with patch.dict(os.environ, {"ARC_AGENT_ENGINE": "legacy"}, clear=True):
            with self.assertRaises(SystemExit) as error:
                main.main([str(self.inputs), "--output-dir", str(self.output)])
        self.assertEqual(error.exception.code, 2)
