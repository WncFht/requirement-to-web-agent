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
