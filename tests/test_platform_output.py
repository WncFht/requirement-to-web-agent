"""Accept initial platform files without trusting or overwriting prior compiler runs."""

from pathlib import Path
import shutil
from tempfile import TemporaryDirectory, mkdtemp
import unittest
from unittest.mock import patch

import main
from infrastructure.shared.project.initialize import initialize_project
from infrastructure.utils.output import application_output, LOCK
from infrastructure.utils.pipeline_state import PipelineState


class PlatformOutputTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(prefix="platform output ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.inputs, self.source, self.output = (
            self.root / name
            for name in ("requirements-source", "submission", "template")
        )
        self.inputs.mkdir()
        self.source.mkdir()
        (self.inputs / "requirements.yaml").write_text(
            "id: REQ-1\nname: Offline\nchildren: []\n"
        )
        # Keep test failure evidence in the test-owned temporary root.
        self.workspace_patch = patch(
            "infrastructure.utils.output.mkdtemp",
            side_effect=lambda **kwargs: mkdtemp(dir=self.root, **kwargs),
        )
        self.workspace_patch.start()
        self.addCleanup(self.workspace_patch.stop)

    def context(self, resume=False):
        return application_output(
            self.output, inputs=self.inputs, source=self.source, resume=resume
        )

    def seed(self):
        initialize_project(self.output)
        (self.output / "frontend/src/App.tsx").write_text("// platform starter\n")
        (self.output / "platform-trace.json").write_text('{"requirements":3}')
        (self.output / ".git").mkdir()
        (self.output / ".git/HEAD").write_text("platform-git")

    def generated(self, output):
        initialize_project(output)
        (output / "frontend/src/App.tsx").write_text("// generated application\n")
        (output / "deploy.sh").write_text("#!/bin/sh\nexit 0\n")
        (output / "deploy.sh").chmod(0o755)

    def test_fresh_destination_and_node_modules_only_keep_direct_workflow(self):
        with self.context() as output:
            self.assertEqual(output, self.output)
        (self.output / "node_modules").mkdir(parents=True)
        with self.context() as output:
            self.assertEqual(output, self.output)

    def test_platform_scaffold_generates_separately_and_publishes_into_original_root(
        self,
    ):
        self.seed()
        inode = self.output.stat().st_ino
        with self.context() as output:
            self.assertNotEqual(output, self.output)
            self.assertEqual(list(output.iterdir()), [])
            self.assertEqual(
                (self.output / "frontend/src/App.tsx").read_text(),
                "// platform starter\n",
            )
            # The actual trusted pipeline now accepts the workspace before Stage 00.
            state = PipelineState(self.source, self.inputs, output, [], False)
            self.assertEqual(state.data["completed"], [])
            self.generated(output)
            workspace = output.parent
        self.assertEqual(self.output.stat().st_ino, inode)
        self.assertEqual(
            (self.output / "frontend/src/App.tsx").read_text(),
            "// generated application\n",
        )
        self.assertEqual((self.output / ".git/HEAD").read_text(), "platform-git")
        self.assertFalse((self.output / LOCK).exists())
        self.assertFalse((self.output / "platform-trace.json").exists())
        self.assertEqual(
            (workspace / "previous-output/platform-trace.json").read_text(),
            '{"requirements":3}',
        )
        self.assertEqual(
            (workspace / "previous-output/frontend/src/App.tsx").read_text(),
            "// platform starter\n",
        )
        self.assertTrue((self.output / "deploy.sh").stat().st_mode & 0o111)

    def test_failed_generation_preserves_seed_and_partial_work_and_removes_lock(self):
        self.seed()
        with self.assertRaisesRegex(RuntimeError, "fixture failure"):
            with self.context() as output:
                (output / "partial.txt").write_text("failure evidence")
                failed_workspace = output
                raise RuntimeError("fixture failure")
        self.assertEqual(
            (failed_workspace / "partial.txt").read_text(), "failure evidence"
        )
        self.assertEqual(
            (self.output / "frontend/src/App.tsx").read_text(), "// platform starter\n"
        )
        self.assertFalse((self.output / LOCK).exists())

    def test_publication_failure_rolls_back_original_files(self):
        self.seed()
        move = shutil.move

        def failed_move(source, target):
            if (
                Path(source).parent.name == "application"
                and Path(source).name == "frontend"
            ):
                raise OSError("publication fixture failure")
            return move(source, target)

        with patch("infrastructure.utils.output.shutil.move", side_effect=failed_move):
            with self.assertRaisesRegex(OSError, "publication fixture failure"):
                with self.context() as output:
                    self.generated(output)
        self.assertEqual(
            (self.output / "frontend/src/App.tsx").read_text(), "// platform starter\n"
        )
        self.assertTrue((self.output / "platform-trace.json").is_file())
        self.assertFalse((self.output / LOCK).exists())

    def test_preinstalled_dependencies_are_copied_without_mutating_seed(self):
        self.seed()
        dependency = self.output / "node_modules/fixture/index.js"
        dependency.parent.mkdir(parents=True)
        dependency.write_text("original")
        with self.assertRaises(RuntimeError):
            with self.context() as output:
                (output / "node_modules/fixture/index.js").write_text(
                    "generated version"
                )
                raise RuntimeError("stop")
        self.assertEqual(dependency.read_text(), "original")

    def test_existing_compiler_output_stays_protected_and_resume_is_explicit(self):
        for name in (
            ".arc/pipeline_state.json",
            ".arc/agent/result.json",
            ".arc/project/report.json",
            ".arc/requirements.json",
        ):
            with self.subTest(marker=name):
                if self.output.exists():
                    shutil.rmtree(self.output)
                marker = self.output / name
                marker.parent.mkdir(parents=True)
                marker.write_text("untouched")
                with self.assertRaisesRegex(ValueError, "Existing compiler output"):
                    with self.context():
                        self.fail("Old run must not be treated as a scaffold")
                self.assertEqual(marker.read_text(), "untouched")
                with self.context(resume=True) as output:
                    self.assertEqual(output, self.output)

    def test_concurrent_writer_and_unsafe_destinations_are_rejected(self):
        self.seed()
        with self.context() as output:
            with self.assertRaisesRegex(ValueError, "lock exists"):
                with self.context():
                    self.fail("Another publisher must not overwrite this run")
            self.generated(output)
        for target in (self.root, self.inputs, self.inputs / "nested", self.source):
            with (
                self.subTest(target=target),
                self.assertRaisesRegex(ValueError, "overlap"),
            ):
                with application_output(target, inputs=self.inputs, source=self.source):
                    self.fail("Unsafe destination accepted")

    def test_real_main_routes_both_engines_through_platform_adapter(self):
        for engine in ("legacy", "coding"):
            with self.subTest(engine=engine):
                if self.output.exists():
                    shutil.rmtree(self.output)
                self.seed()

                def generate(source, inputs, output, port, chosen, resume):
                    self.assertEqual(chosen, engine)
                    self.assertEqual(inputs, self.inputs)
                    self.assertNotEqual(output, self.output)
                    self.generated(output)

                import os
                import sys

                with (
                    patch.object(
                        sys,
                        "argv",
                        ["main.py", str(self.inputs), "--output-dir", str(self.output)],
                    ),
                    patch.dict(os.environ, {"ARC_AGENT_ENGINE": engine}, clear=True),
                    patch.object(main, "generate_application", side_effect=generate),
                ):
                    main.main()
                self.assertEqual(
                    (self.output / "frontend/src/App.tsx").read_text(),
                    "// generated application\n",
                )
