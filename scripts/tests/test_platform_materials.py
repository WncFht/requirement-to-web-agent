"""Keep published assertions immutable; reject unsafe archives and false local GREEN."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from platform_materials import extract, materialize, report_status, verify


class PlatformMaterialsTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.snapshot = self.root / "snapshot"
        self.snapshot.mkdir()
        self.files = {}
        raw = b"id: ROOT\nchildren: []\n"
        self.write("tasks/task/input/requirements.yaml", raw)
        self.write(
            "tasks/task/task.json",
            json.dumps({"requirements_yaml": raw.decode()}).encode(),
        )
        assertion = b"test('original', async () => {});\n"
        self.write("tasks/task/acceptance/test.spec.ts", assertion)
        self.write(
            "tasks/task/tests.json",
            json.dumps(
                {"files": [{"path": "test.spec.ts", "content": assertion.decode()}]}
            ).encode(),
        )
        self.write("tasks/task/docs/requirements.md", b"# Original requirement\n")
        archive = self.snapshot / "archive.zip"
        with zipfile.ZipFile(archive, "w") as bundle:
            bundle.writestr("task/requirements.yaml", raw)
            bundle.writestr("task/reference/image.png", b"sample-image")
            bundle.writestr("unrelated/requirements.yaml", b"other task")
        self.register("archive.zip", "official_archive")
        self.task = {
            "task_id": "task",
            "metadata": "tasks/task/task.json",
            "input_yaml": "tasks/task/input/requirements.yaml",
            "reference_archive": "archive.zip",
            "requirements_sha256": hashlib.sha256(raw).hexdigest(),
            "acceptance": "tasks/task/acceptance",
            "test_response": "tasks/task/tests.json",
            "tests_available": True,
            "platform_test_count": 1,
        }
        self.save()

    def register(self, name, kind="official_test"):
        path = self.snapshot / name
        self.files[name] = {
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "bytes": path.stat().st_size,
            "kind": kind,
        }

    def write(self, name, content):
        path = self.snapshot / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        self.register(name)

    def save(self):
        (self.snapshot / "manifest.json").write_text(
            json.dumps({"schema_version": 1, "files": self.files, "tasks": [self.task]})
        )

    def test_materialization_separates_inputs_from_assertions_and_refuses_overwrite(
        self,
    ):
        output, record = materialize("task", self.root / "run", self.snapshot)
        self.assertTrue((output / "input/reference/image.png").is_file())
        self.assertFalse((output / "input/tests").exists())
        self.assertFalse((output / "input/unrelated").exists())
        self.assertEqual(
            (output / "acceptance/test.spec.ts").read_bytes(),
            (self.snapshot / "tasks/task/acceptance/test.spec.ts").read_bytes(),
        )
        self.assertFalse(record["tests_executed"])
        with self.assertRaisesRegex(ValueError, "overwrite"):
            materialize("task", output, self.snapshot)

    def test_tampering_extra_files_and_lfs_pointers_are_rejected(self):
        path = self.snapshot / "tasks/task/acceptance/test.spec.ts"
        original = path.read_bytes()
        path.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            verify(self.snapshot)
        path.write_bytes(original)
        extra = self.snapshot / "extra.spec.ts"
        extra.write_text("extra")
        with self.assertRaisesRegex(ValueError, "member set"):
            verify(self.snapshot)
        extra.unlink()
        (self.snapshot / "archive.zip").write_text(
            "version https://git-lfs.github.com/spec/v1\n"
        )
        with self.assertRaisesRegex(ValueError, "Git LFS"):
            verify(self.snapshot)

    def test_hidden_tests_are_not_fabricated(self):
        self.task["tests_available"] = False
        self.save()
        output, record = materialize("task", self.root / "hidden", self.snapshot)
        self.assertFalse(record["tests_available"])
        self.assertFalse((output / "acceptance").exists())

    def test_zip_traversal_and_symlink_are_rejected(self):
        archive = self.root / "bad.zip"
        with zipfile.ZipFile(archive, "w") as bundle:
            bundle.writestr("../escape", "bad")
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            extract(archive, self.root / "extracted")
        with zipfile.ZipFile(archive, "w") as bundle:
            entry = zipfile.ZipInfo("link")
            entry.external_attr = 0o120777 << 16
            bundle.writestr(entry, "outside")
        with self.assertRaisesRegex(ValueError, "symlink"):
            extract(archive, self.root / "extracted")

    def test_collection_is_not_a_pass_and_green_requires_all_cases(self):
        report = {
            "suites": [{"specs": [{"tests": [{}]}]}],
            "stats": {"expected": 1, "skipped": 0, "flaky": 0, "unexpected": 0},
        }
        self.assertEqual(report_status(report, 0, True, 1), "COLLECTED")
        self.assertEqual(report_status(report, 0, False, 1), "LOCAL_PUBLIC_TESTS_GREEN")
        for kind in ("skipped", "unexpected", "flaky"):
            broken = deepcopy(report)
            broken["stats"][kind] = 1
            self.assertEqual(report_status(broken, 0, False, 1), "FAILED")
        self.assertEqual(report_status(report, 0, False, 2), "FAILED")
        self.assertEqual(report_status({"suites": []}, 0, False, 0), "FAILED")
        self.assertEqual(report_status(report | {"errors": [{}]}, 0, True, 1), "FAILED")
