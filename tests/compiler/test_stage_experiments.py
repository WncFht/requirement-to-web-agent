"""Stage inputs and budget stop rules cannot silently reuse success or incur calls."""

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from infrastructure.shared.agent.checkpoints import capture, restore
from infrastructure.shared.agent.experiment_budget import (
    reserve,
    finish,
    ExperimentBudgetExceeded,
)


class StageExperimentTests(unittest.TestCase):
    def test_checkpoint_exact_bytes_and_tampering_before_restore(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            app = root / "app"
            (app / ".arc").mkdir(parents=True)
            (app / ".arc/compilation.json").write_text('{"status":"GREEN"}')
            (app / "backend").mkdir()
            (app / "backend/app.ts").write_bytes(b"original\r\n")
            (app / ".env").write_text("SECRET=fixture")
            (app / "app.db").write_bytes(b"private database")
            checkpoint = root / "checkpoint"
            manifest = capture(app, checkpoint)
            self.assertNotIn(".env", manifest["files"])
            self.assertNotIn("app.db", manifest["files"])
            restore(checkpoint, root / "restored")
            self.assertEqual(
                (root / "restored/backend/app.ts").read_bytes(), b"original\r\n"
            )
            self.assertFalse((root / "restored/.arc/compilation.json").exists())
            with self.assertRaises(FileExistsError):
                restore(checkpoint, root / "restored")
            (checkpoint / "application/backend/app.ts").write_text("tampered")
            with self.assertRaisesRegex(ValueError, "mismatch"):
                restore(checkpoint, root / "bad")
            self.assertFalse((root / "bad").exists())

    def test_unknown_usage_pending_deadline_and_limits_block_calls(self):
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "budget.json"
            initial = {
                "calls": 0,
                "max_calls": 2,
                "total_tokens": 0,
                "max_tokens": 100,
                "deadline_utc": (
                    datetime.now(timezone.utc) + timedelta(seconds=60)
                ).isoformat(),
            }
            with patch.dict(os.environ, {"ARC_EXPERIMENT_BUDGET": str(path)}):
                path.write_text(json.dumps(initial))
                token = reserve()
                with self.assertRaises(ExperimentBudgetExceeded):
                    reserve()
                finish(token, {"total_tokens": 60})
                finish(reserve(), {"total_tokens": 60})
                with self.assertRaises(ExperimentBudgetExceeded):
                    reserve()
                path.write_text(json.dumps(initial))
                finish(reserve(), None)
                with self.assertRaises(ExperimentBudgetExceeded):
                    reserve()
                initial["deadline_utc"] = (
                    datetime.now(timezone.utc) - timedelta(seconds=1)
                ).isoformat()
                path.write_text(json.dumps(initial))
                with self.assertRaises(ExperimentBudgetExceeded):
                    reserve()


class ContextCandidateTests(unittest.TestCase):
    def test_import_closure_permissions_and_input_are_preserved(self):
        from copy import deepcopy
        from infrastructure.shared.agent.context_candidate import select_related

        payload = {
            "task": {"id": "home"},
            "feedback": [{"error": "keep me"}],
            "files": {
                "frontend/src/home.tsx": {
                    "content": 'import { helper } from "./helper.js";',
                    "writable": True,
                },
                "frontend/src/helper.ts": {
                    "content": "export const helper = 1;",
                    "writable": False,
                },
                "frontend/src/register.tsx": {
                    "content": "unrelated form",
                    "writable": True,
                },
                "frontend/tests/home.spec.ts": {"content": "frozen", "writable": False},
            },
        }
        original = deepcopy(payload)
        selected, report = select_related(payload, ["frontend/src/home.tsx"])
        self.assertEqual(payload, original)
        self.assertEqual(selected["task"], payload["task"])
        self.assertEqual(selected["feedback"], payload["feedback"])
        self.assertFalse(selected["files"]["frontend/src/helper.ts"]["writable"])
        self.assertFalse(selected["files"]["frontend/tests/home.spec.ts"]["writable"])
        self.assertEqual(report["omitted"], ["frontend/src/register.tsx"])


class StageWindowTests(unittest.TestCase):
    def test_actual_no_ui_stage_window_has_no_model_calls_or_reused_green(self):
        import sys
        from unittest.mock import patch

        root = Path(__file__).resolve().parents[2]
        sys.path.insert(0, str(root / "scripts"))
        from stage_replay import window

        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            app = directory / "app"
            (app / ".arc").mkdir(parents=True)
            (app / ".arc/requirements.json").write_text(
                json.dumps({"id": "ROOT", "children": []})
            )
            (app / ".arc/visual_analysis.json").write_text("{}")
            (app / ".arc/ui_design.json").write_text(
                json.dumps(
                    {
                        "pages": {},
                        "elements": {},
                        "bindings": {},
                        "requirements": {},
                        "steps": {},
                    }
                )
            )
            (app / ".arc/compilation.json").write_text('{"status":"GREEN"}')
            checkpoint = directory / "checkpoint"
            capture(app, checkpoint, stage="10_implement_ui")
            ledger = directory / "budget.json"
            ledger.write_text('{"calls":0,"max_output_tokens":64000}')
            with (
                patch.dict(os.environ, {}, clear=False),
                patch("stage_replay.ROOT", directory),
            ):
                output = directory / "work/replay"
                result = window(checkpoint, output, directory, 10, 10, ledger)
            self.assertEqual(result["status"], "GREEN")
            self.assertFalse(result["complete_generation"])
            self.assertFalse((output / ".arc/compilation.json").exists())
            self.assertEqual(json.loads(ledger.read_text())["calls"], 0)
            record = json.loads((checkpoint / "checkpoint.json").read_text())
            record["stage"] = None
            (checkpoint / "checkpoint.json").write_text(json.dumps(record))
            with (
                patch("stage_replay.ROOT", directory),
                self.assertRaisesRegex(ValueError, "named starting stage"),
            ):
                window(
                    checkpoint, directory / "work/invalid", directory, 10, 10, ledger
                )
            self.assertFalse((directory / "work/invalid").exists())


class BudgetHeadroomTests(unittest.TestCase):
    def test_cap_closed_and_previous_prompt_headroom(self):
        from infrastructure.shared.agent.experiment_budget import limit_arguments

        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "budget.json"
            record = {
                "calls": 0,
                "max_calls": 6,
                "total_tokens": 60,
                "max_tokens": 100,
                "last_prompt_tokens": 30,
                "max_output_tokens": 20,
                "deadline_utc": (
                    datetime.now(timezone.utc) + timedelta(seconds=60)
                ).isoformat(),
            }
            path.write_text(json.dumps(record))
            with patch.dict(os.environ, {"ARC_EXPERIMENT_BUDGET": str(path)}):
                args = limit_arguments({"max_completion_tokens": 1000})
                self.assertEqual(args["max_completion_tokens"], 20)
                with self.assertRaisesRegex(ExperimentBudgetExceeded, "headroom"):
                    reserve(args)
                record["closed"] = True
                path.write_text(json.dumps(record))
                with self.assertRaisesRegex(ExperimentBudgetExceeded, "closed"):
                    reserve()


class OutputAllowanceTests(unittest.TestCase):
    def test_default_allowance_and_timeout_do_not_repeat_old_experiment_cap(self):
        import sys

        sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
        from stage_replay import budget
        from infrastructure.shared.agent.experiment_budget import (
            limit_arguments,
            request_timeout,
        )

        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "budget.json"
            record = budget(path, calls=1, tokens=100000)
            self.assertEqual(record["max_output_tokens"], 64000)
            with patch.dict(os.environ, {"ARC_EXPERIMENT_BUDGET": str(path)}):
                self.assertEqual(
                    limit_arguments({"max_completion_tokens": 64000})[
                        "max_completion_tokens"
                    ],
                    64000,
                )
                self.assertEqual(request_timeout(), 600)
                finish(
                    reserve({"max_completion_tokens": 64000}), {"total_tokens": 25000}
                )
                with self.assertRaises(ExperimentBudgetExceeded):
                    reserve()
            with self.assertRaises(ValueError):
                budget(Path(temporary) / "bad.json", tokens=10000, output_tokens=64000)
