"""Queued cache work must fail closed instead of overlapping/restarting incomplete primary trials."""

import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import followup_cache_campaign


class CacheFollowupQueueTests(unittest.TestCase):
    def run_fixture(self, mode):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "cache-followup-protocol.json").write_text(
                json.dumps({"candidate_revision": "registered"})
            )
            if mode == "dead":
                (root / "runner.lock").write_text("999999999")
            elif mode in {"incomplete_marker", "wrong_candidate"}:
                (root / "complete.json").write_text("{}")
            argv = [
                "followup_cache_campaign.py",
                "--campaign",
                str(root),
                "--candidate-source",
                str(root),
                "--node-bin",
                str(root),
                "--source-log",
                str(root / "log"),
            ]
            with (
                patch.object(sys, "argv", argv),
                patch.object(
                    followup_cache_campaign,
                    "summarize",
                    return_value={"complete": mode == "wrong_candidate", "arms": {}},
                ),
                patch.object(followup_cache_campaign, "git", return_value="changed"),
                patch.object(followup_cache_campaign.subprocess, "run") as model_work,
            ):
                with self.assertRaises(ValueError):
                    followup_cache_campaign.main()
                model_work.assert_not_called()

    def test_missing_primary_lock_does_not_restart_or_start_model_work(self):
        self.run_fixture("missing")

    def test_vanished_primary_process_does_not_start_model_work(self):
        self.run_fixture("dead")

    def test_completion_marker_without_all_results_does_not_start_followup(self):
        self.run_fixture("incomplete_marker")

    def test_candidate_revision_change_is_rejected_before_model_work(self):
        self.run_fixture("wrong_candidate")
