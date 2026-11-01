"""Independent acceptance fails closed when original inputs or adapters are unknown."""

import hashlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import accept_teacher


class TeacherAcceptanceTests(unittest.TestCase):
    def test_original_test_tampering_is_rejected(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "input/tests").mkdir(parents=True)
            path = root / "input/tests/REQ-1.spec.ts"
            path.write_text("frozen assertion")
            manifest = {
                "files": {
                    "tests/REQ-1.spec.ts": hashlib.sha256(path.read_bytes()).hexdigest()
                }
            }
            (root / "input/source.json").write_text(json.dumps(manifest))
            with patch.object(accept_teacher, "ROOT", root):
                self.assertEqual(accept_teacher.verify_input(), manifest)
                path.write_text("relaxed assertion")
                with self.assertRaisesRegex(ValueError, "Teacher input changed"):
                    accept_teacher.verify_input()

    def test_unknown_storage_schema_requires_explicit_review(self):
        with TemporaryDirectory() as folder:
            output = Path(folder)
            (output / ".arc").mkdir()
            (output / ".arc/db_schema.json").write_text(json.dumps({"entities": {}}))
            with self.assertRaisesRegex(ValueError, "review"):
                accept_teacher.make_adapter(output)
