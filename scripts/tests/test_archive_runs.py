"""Dependency pruning must follow a byte-verified evidence archive."""

import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from archive_runs import archive


class ArchiveRunTests(unittest.TestCase):
    def test_evidence_is_verified_before_dependencies_are_removed(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            run = root / "sample"
            (run / ".arc").mkdir(parents=True)
            (run / ".arc/report.json").write_text(json.dumps({"status": "FAILED"}))
            (run / "node_modules").mkdir()
            (run / "node_modules/rebuildable.txt").write_text("dependency")
            (run / ".env").write_text("PRIVATE_LOCAL_CONFIG=fixture")
            result = archive(run, root / "archives", prune=True)
            self.assertEqual(result["verified_files"], 1)
            self.assertTrue(result["dependencies_pruned"])
            self.assertFalse((run / "node_modules").exists())
            self.assertTrue((run / ".env").exists())
            with self.assertRaisesRegex(ValueError, "overwrite"):
                archive(run, root / "archives")
