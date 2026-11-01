"""Exercise trusted completion separately from partial artifacts and failed gates."""

from contextlib import ExitStack
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import run_all
from infrastructure.utils.files import save_json
from infrastructure.utils.pipeline_state import (
    PipelineState,
    STATE,
    identity,
    pipeline_lock,
    validate_completion,
    workspace,
)


class PipelineResumeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source, self.inputs, self.output = (
            self.root / name for name in ("source", "input", "output")
        )
        for path in (self.source, self.inputs, self.output):
            path.mkdir()
        (self.inputs / "requirements.yaml").write_text("requirements: teacher\n")
        (self.source / "run_all.py").write_text("# compiler\n")
        self.steps = run_all.STEPS
        self.calls = []
        self.failure = None
        self.patches = ExitStack()
        self.addCleanup(self.patches.close)
        self.patches.enter_context(
            patch.dict(os.environ, {"ARC_LEGACY_PIPELINE_RESUME": "0"})
        )
        self.patches.enter_context(patch.object(run_all, "COMPILER_DIR", self.source))
        self.patches.enter_context(patch.object(run_all, "show_panel"))

    def write(self, relative, value):
        path = self.output / relative
        if isinstance(value, dict):
            save_json(path, value)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value)

    def artifact(self, step):
        number = int(step[:2])
        artifacts = {
            0: ("package.json", {}),
            1: (
                ".arc/requirements.json",
                {
                    "id": "REQ-1",
                    "name": "teacher",
                    "description": "",
                    "children": [],
                    "steps": [],
                },
            ),
            2: (
                ".arc/db_schema.json",
                {
                    "entities": {"User": {}, "Session": {}},
                    "requirements": {"REQ-1": []},
                },
            ),
            3: (".arc/db_obligations.json", {}),
            6: (".arc/backend_apis.json", {}),
            7: (".arc/backend_contracts.json", {"apis": {"login": {}}}),
            8: (".arc/backend_tdd.json", {"status": "GREEN"}),
            9: (".arc/ui_design.json", {"pages": {"home": {}}}),
            10: (".arc/ui_checks.json", {"status": "GREEN"}),
            11: (".arc/ui_interactions.json", {}),
            12: (".arc/frontend_e2e.json", {"status": "GREEN"}),
        }
        if number in artifacts:
            self.write(*artifacts[number])
        if number == 1:
            self.write(".arc/visual_analysis.json", {})
        if number == 5:
            for name in ("User", "Session"):
                self.write(f"backend/src/db/tables/{name}.sql", f"CREATE TABLE {name};")
            self.write("backend/src/db/initialize.ts", "// generated registry")
        if number == 10:
            self.write("frontend/src/page.tsx", "// initial page")
        if number == 12:
            self.write("frontend/src/page.tsx", "// downstream page with interactions")

    def start(self, command, **kwargs):
        step = Path(command[1]).name
        self.calls.append(step)
        self.artifact(step)
        if step == self.failure:
            # Partial content and old successful-looking reports are not receipts.
            self.write(".arc/ui_design_progress.json", {"completed": ["REQ-1"]})
            return type("Child", (), {"wait": lambda _: 1})()
        return type("Child", (), {"wait": lambda _: 0})()

    def run_pipeline(self, resume=False):
        with patch.object(run_all, "start_process", side_effect=self.start):
            run_all.run_pipeline(self.inputs, self.output, resume)

    def state(self):
        return json.loads((self.output / STATE).read_text())

    def test_full_completion_skips_all_and_accepts_downstream_edits(self):
        self.run_pipeline()
        self.assertEqual(self.calls, list(self.steps))
        self.calls.clear()
        self.run_pipeline(resume=True)
        self.assertEqual(self.calls, [])
        self.assertEqual(self.state()["completed"], list(self.steps))

    def test_every_failed_stage_is_reentered_not_promoted_from_artifacts(self):
        for index, step in enumerate(self.steps):
            with self.subTest(step=step):
                self.output = self.root / f"run-{index}"
                self.output.mkdir()
                self.failure = step
                with self.assertRaises(subprocess.CalledProcessError):
                    self.run_pipeline()
                self.assertEqual(self.state()["completed"], list(self.steps[:index]))
                self.assertIsNone(self.state()["active"])
                self.assertFalse((self.output / ".arc/pipeline.lock").exists())
                self.failure, self.calls = None, []
                self.run_pipeline(resume=True)
                self.assertEqual(self.calls, list(self.steps[index:]))

    def test_partial_schema_missing_requirement_is_not_complete(self):
        self.artifact(self.steps[1])
        self.write(".arc/db_schema.json", {"entities": {}, "requirements": {}})
        with self.assertRaisesRegex(ValueError, "every leaf"):
            validate_completion(self.output, self.steps[2])

    def test_one_sql_file_cannot_complete_a_two_table_stage(self):
        self.artifact(self.steps[2])
        self.write("backend/src/db/tables/User.sql", "CREATE TABLE User;")
        with self.assertRaisesRegex(ValueError, "Session.sql"):
            validate_completion(self.output, self.steps[5])

        self.write("backend/src/db/tables/Session.sql", "CREATE TABLE Session;")
        with self.assertRaisesRegex(ValueError, "initialize.ts"):
            validate_completion(self.output, self.steps[5])

    def test_empty_schema_requires_initializer_but_no_sql(self):
        self.write(".arc/db_schema.json", {"entities": {}})
        with self.assertRaisesRegex(ValueError, "initialize.ts"):
            validate_completion(self.output, self.steps[5])
        self.write("backend/src/db/initialize.ts", "// empty registry")
        validate_completion(self.output, self.steps[5])

    def test_zero_exit_failed_ui_gate_does_not_publish_completion(self):
        original = self.artifact

        def failed_ui(step):
            original(step)
            if step == self.steps[10]:
                self.write(".arc/ui_checks.json", {"status": "FAILED"})

        with patch.object(self, "artifact", side_effect=failed_ui):
            with self.assertRaisesRegex(ValueError, "completion requires GREEN"):
                self.run_pipeline()
        self.assertEqual(self.state()["completed"], list(self.steps[:10]))
        self.assertIsNone(self.state()["active"])
        self.calls.clear()
        self.run_pipeline(resume=True)
        self.assertEqual(self.calls, list(self.steps[10:]))

    def test_no_ui_and_no_apis_only_pass_with_empty_design(self):
        for number, report, status, design, key in (
            (8, "backend_tdd", "NO_APIS", "backend_contracts", "apis"),
            (10, "ui_checks", "NO_UI", "ui_design", "pages"),
            (12, "frontend_e2e", "NO_UI", "ui_design", "pages"),
        ):
            self.write(f".arc/{report}.json", {"status": status})
            self.write(f".arc/{design}.json", {key: {"exists": {}}})
            with self.assertRaises(ValueError):
                validate_completion(self.output, self.steps[number])
            self.write(f".arc/{design}.json", {key: {}})
            validate_completion(self.output, self.steps[number])

    def test_changed_input_source_configuration_or_output_preserves_old_files(self):
        for kind in (
            "input",
            "source",
            "configuration",
            "artifact",
            "deleted",
            "added",
        ):
            with self.subTest(kind=kind):
                self.output = self.root / ("case-" + kind)
                self.output.mkdir()
                self.run_pipeline()
                with ExitStack() as changes:
                    if kind in {"input", "source"}:
                        target = (
                            self.inputs / "requirements.yaml"
                            if kind == "input"
                            else self.source / "run_all.py"
                        )
                        before = target.read_bytes()
                        changes.callback(target.write_bytes, before)
                        target.write_text("changed")
                    elif kind == "configuration":
                        changes.enter_context(
                            patch.dict(os.environ, {"MODEL": "another-model"})
                        )
                    elif kind == "deleted":
                        (self.output / "backend/src/db/tables/User.sql").unlink()
                    else:
                        self.write(
                            "frontend/src/page.tsx"
                            if kind == "artifact"
                            else "frontend/src/new.ts",
                            "user work",
                        )
                    sealed = (self.output / STATE).read_bytes()
                    self.calls.clear()
                    with self.assertRaisesRegex(ValueError, "new --output"):
                        self.run_pipeline(resume=True)
                    self.assertEqual(self.calls, [])
                    self.assertEqual((self.output / STATE).read_bytes(), sealed)

    def test_credentials_not_persisted_or_used_to_invalidate(self):
        self.run_pipeline()
        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "private-value", "VISUAL_API_KEY": "other-private"},
        ):
            self.run_pipeline(resume=True)
        self.assertNotIn("private", (self.output / STATE).read_text())

    def test_dotenv_configuration_invalidation_but_key_rotation_allowed(self):
        env_file = self.source / ".env"
        env_file.write_text("MODEL=first\nOPENAI_API_KEY=private-1\n")
        with patch.dict(os.environ, {}, clear=True):
            first = identity(self.source, self.inputs)
            env_file.write_text("MODEL=first\nOPENAI_API_KEY=private-2\n")
            self.assertEqual(first, identity(self.source, self.inputs))
            env_file.write_text("MODEL=second\nOPENAI_API_KEY=private-2\n")
            self.assertNotEqual(first, identity(self.source, self.inputs))

    def test_old_sentinels_and_corrupt_state_are_never_automatically_adopted(self):
        self.artifact(self.steps[0])
        with self.assertRaisesRegex(ValueError, "no trusted"):
            self.run_pipeline(resume=True)
        self.write(STATE, "{broken")
        with self.assertRaisesRegex(ValueError, "Cannot reuse"):
            self.run_pipeline(resume=True)

    def test_concurrent_writer_and_hard_kill_fail_closed(self):
        with pipeline_lock(self.output):
            with self.assertRaisesRegex(ValueError, "lock exists"):
                self.run_pipeline()
        state = PipelineState(self.source, self.inputs, self.output, self.steps, False)
        state.begin(self.steps[0])
        self.artifact(self.steps[0])
        with self.assertRaisesRegex(ValueError, "without sealing"):
            self.run_pipeline(resume=True)

    def test_normal_interrupt_stops_child_then_seals_partial_work(self):
        child = type(
            "Child", (), {"wait": lambda _: (_ for _ in ()).throw(KeyboardInterrupt())}
        )()

        def start(*args, **kwargs):
            self.artifact(self.steps[0])
            return child

        with (
            patch.object(run_all, "start_process", side_effect=start),
            patch.object(run_all, "stop_process") as stopped,
        ):
            with self.assertRaises(KeyboardInterrupt):
                run_all.run_pipeline(self.inputs, self.output, False)
            stopped.assert_called_once_with(child)
        self.assertEqual(self.state()["completed"], [])
        self.assertIsNone(self.state()["active"])
        self.run_pipeline(resume=True)

    def test_runtime_evidence_and_dependencies_do_not_change_workspace_seal(self):
        self.run_pipeline()
        before = workspace(self.output)
        for relative in (
            "compiler.log",
            "model_calls.jsonl",
            "deploy.sh",
            "node_modules/cache.json",
            "frontend/dist/build.js",
            ".arc/teacher-acceptance/run/summary.json",
            "frontend/tests/fixed-review/fixed.spec.ts",
            "frontend/vite.fixed.config.ts",
            "backend/data/app.db",
        ):
            self.write(relative, "runtime evidence")
        self.assertEqual(before, workspace(self.output))
        self.run_pipeline(resume=True)

    def test_failed_child_cleanup_leaves_untrusted_active_state(self):
        child = type(
            "Child", (), {"wait": lambda _: (_ for _ in ()).throw(KeyboardInterrupt())}
        )()
        with (
            patch.object(run_all, "start_process", return_value=child),
            patch.object(
                run_all, "stop_process", side_effect=OSError("cleanup failed")
            ),
        ):
            with self.assertRaisesRegex(OSError, "cleanup failed"):
                run_all.run_pipeline(self.inputs, self.output, False)
        self.assertEqual(self.state()["active"], self.steps[0])
        with self.assertRaisesRegex(ValueError, "without sealing"):
            self.run_pipeline(resume=True)

    def test_changed_code_during_stage_cannot_get_a_receipt(self):
        def start(command, **kwargs):
            self.artifact(self.steps[0])
            (self.source / "run_all.py").write_text("edited while running")
            return type("Child", (), {"wait": lambda _: 0})()

        with patch.object(run_all, "start_process", side_effect=start):
            with self.assertRaisesRegex(ValueError, "changed during execution"):
                run_all.run_pipeline(self.inputs, self.output, False)
        self.assertEqual(self.state()["completed"], [])
        self.assertEqual(self.state()["active"], self.steps[0])

    def test_legacy_flag_explicitly_keeps_old_sentinel_behavior(self):
        self.artifact(self.steps[0])
        with (
            patch.dict(os.environ, {"ARC_LEGACY_PIPELINE_RESUME": "1"}),
            patch.object(run_all, "STEPS", (self.steps[0],)),
        ):
            self.run_pipeline(resume=True)
        self.assertEqual(self.calls, [])
        self.assertFalse((self.output / STATE).exists())

    def test_real_subprocess_failure_resume_and_noop(self):
        # Deterministic child fixtures exercise the actual process/CLI boundary,
        # with no model calls and no altered teacher input or acceptance tests.
        fixtures = self.root / "fixture-files"
        fixtures.mkdir()
        output, self.output = self.output, fixtures
        try:
            before = {}
            for step in self.steps:
                self.artifact(step)
                after = workspace(fixtures)
                changed = {
                    name: (fixtures / name).read_text()
                    for name in after
                    if after.get(name) != before.get(name)
                }
                (self.source / step).write_text(
                    "import argparse,os,pathlib,sys\n"
                    "p=argparse.ArgumentParser();p.add_argument('--input');p.add_argument('--output');p.add_argument('--no-browse',action='store_true');a=p.parse_args()\n"
                    "root=pathlib.Path(a.output);root.mkdir(parents=True,exist_ok=True)\n"
                    f"files={changed!r}\n"
                    "for name,content in files.items():\n path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(content)\n"
                    f"with (root/'child-calls.log').open('a') as f: f.write({step!r}+'\\n')\n"
                    f"sys.exit(7 if os.getenv('PIPELINE_TEST_FAIL')=={step!r} else 0)\n"
                )
                before = after
        finally:
            self.output = output
        with patch.dict(os.environ, {"PIPELINE_TEST_FAIL": self.steps[9]}):
            with self.assertRaises(subprocess.CalledProcessError):
                run_all.run_pipeline(self.inputs, self.output, False)
        self.assertEqual(self.state()["completed"], list(self.steps[:9]))
        run_all.run_pipeline(self.inputs, self.output, True)
        calls = (self.output / "child-calls.log").read_text().splitlines()
        self.assertEqual(calls, list(self.steps[:10]) + list(self.steps[9:]))
        run_all.run_pipeline(self.inputs, self.output, True)
        self.assertEqual(
            (self.output / "child-calls.log").read_text().splitlines(), calls
        )

    def test_real_stage_zero_scaffold_and_resume(self):
        with (
            patch.object(run_all, "COMPILER_DIR", Path(run_all.__file__).parent),
            patch.object(run_all, "STEPS", (self.steps[0],)),
        ):
            run_all.run_pipeline(self.inputs, self.output, False)
            self.assertTrue((self.output / "backend/src/server.ts").is_file())
            self.assertEqual(self.state()["completed"], [self.steps[0]])
            with patch.object(run_all, "start_process") as start:
                run_all.run_pipeline(self.inputs, self.output, True)
                start.assert_not_called()

    def test_symlink_metadata_and_output_escape_are_rejected(self):
        outside = self.root / "outside"
        outside.mkdir()
        try:
            (self.output / ".arc").symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("Host cannot create symlinks")
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.run_pipeline()
        (self.output / ".arc").unlink()
        self.run_pipeline()
        file = self.output / "frontend/src/page.tsx"
        file.unlink()
        (outside / "page.tsx").write_text("outside")
        file.symlink_to(outside / "page.tsx")
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            self.run_pipeline(resume=True)
