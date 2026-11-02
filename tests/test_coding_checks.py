"""Admission and real Node/browser regressions; never calls a paid model."""

import os
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from urllib.request import urlopen

from coding_agent.checks import (
    application_environment,
    validate_tests,
    prepare_project,
    Checks,
)
from coding_agent.config import Config
from coding_agent.loop import run
from coding_agent.protocol import InvalidTest
from coding_agent.trace import audit
from coding_agent.acceptance import servers
from coding_fixture import FixtureModel, SETUP, REFERENCE_IMAGE


class CodingChecksTests(unittest.TestCase):
    def test_assertion_failure_does_not_hide_another_backend_runtime_error(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, source in SETUP.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(source)
            checks = Checks(root)
            checks.required_ids = []
            reports = [
                {"returncode": 0, "passed": 1},
                {
                    "returncode": 1,
                    "passed": 0,
                    "failed": 2,
                    "output": "  code: 'ERR_ASSERTION'\n  name: 'AssertionError'\n  name: 'TypeError'\n",
                },
            ]
            with patch.object(checks, "run", side_effect=reports):
                with self.assertRaisesRegex(ValueError, "backend: need assertion RED"):
                    checks.freeze()

    def test_application_process_cannot_inherit_model_credentials(self):
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "fixture",
                "VISUAL_API_KEY": "fixture",
                "MODEL": "fixture",
                "PATH": "/bin",
            },
            clear=True,
        ):
            env = application_environment({"DATABASE_URL": "/tmp/isolated.db"})
        self.assertEqual(env, {"PATH": "/bin", "DATABASE_URL": "/tmp/isolated.db"})

    def test_known_contradictions_rejected_before_freezing(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, source in SETUP.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(source)
            target = root / "frontend/tests/e2e/workflows.spec.ts"
            for source in [
                'test("existing session signed in",async()=>{seedExistingSession(database);await page.goto("/");await expect(user).toHaveText("fixture")});',
                'test("gender",async()=>{await female.check();await male.check();expect(row.gender).toBe("Female");});',
                'test.skip("ignored",async()=>{});',
            ]:
                target.write_text(source)
                with self.subTest(source=source), self.assertRaises(InvalidTest):
                    validate_tests(root)

    @unittest.skipUnless(
        os.environ.get("ARC_RUN_BROWSER_TESTS") == "1",
        "Explicit local Node22/browser integration suite",
    )
    def test_real_cross_layer_loop_freezes_tests_and_recovers_a_frontend_regression(
        self,
    ):
        snapshot = Path(os.environ["ARC_TEST_DEPENDENCIES"])
        with TemporaryDirectory(prefix="coding-loop-integration-") as tmp:
            root = Path(tmp)
            inputs = root / "input"
            inputs.mkdir()
            (inputs / "requirements.yaml").write_text(
                "id: REQ-1\nname: Notes\nchildren: []\n"
            )
            (inputs / "reference.png").write_bytes(REFERENCE_IMAGE)
            output = root / "output"
            output.mkdir()
            shutil.copytree(snapshot, output / "node_modules", symlinks=True)
            config = Config(
                inputs,
                output,
                base_url="http://unused.invalid",
                api_key="unused-fixture",
                max_turns=8,
                max_seconds=180,
            )
            result = run(config, model_factory=FixtureModel)
            self.assertEqual(result["status"], "INTERNAL_GREEN", result)
            self.assertEqual(result["turns"], 6)
            self.assertTrue(audit(output)["valid"])
            self.assertTrue(result["frozen_tests"])
            with servers(output, root, "production") as (base, _):
                with urlopen(base + "/assets/reference.png", timeout=5) as response:
                    self.assertEqual(response.read(), REFERENCE_IMAGE)
            saved = list((output / ".arc/agent/artifacts").glob("browser-*"))
            images = [p for folder in saved for p in folder.rglob("*.png")]
            self.assertGreaterEqual(len(saved), 3)
            self.assertTrue(
                images, "Original failed-check screenshots must survive later checks"
            )
            images[0].write_bytes(b"altered diagnostic")
            self.assertFalse(audit(output)["valid"])


if __name__ == "__main__":
    unittest.main()
