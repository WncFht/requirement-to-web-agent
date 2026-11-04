"""Offline controls for test semantics and implementation/test ownership."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock

from infrastructure.shared.agent.admission import (
    validate_backend_test,
    validate_e2e_test,
    validate_ui_controls,
)
from infrastructure.shared.agent.files import FileWorkspace
from infrastructure.shared.agent.frozen_tests import (
    freeze_tests,
    verify_frozen_tests,
    FrozenTestViolation,
)
from infrastructure.shared.agent.recovery import implementation_task
from infrastructure.stages.frontend.ui.testing import existence_suite


def radio_design():
    return {
        "pages": {
            "register": {
                "root": "page",
                "route": "/register",
                "fixtures": {
                    "empty": {},
                    "male": {"gender": "Male"},
                    "female": {"gender": "Female"},
                },
            }
        },
        "bindings": {"gender": {"initial": ""}},
        "elements": {
            "page": {
                "type": "page",
                "children": ["male", "female"],
                "data": [],
                "prop": {},
            },
            **{
                name.lower(): {
                    "type": "input",
                    "parent": "page",
                    "data": ["gender"],
                    "prop": {"input_type": "radio", "value": name, "label": name},
                }
                for name in ("Male", "Female")
            },
        },
    }


class AdmissionTests(unittest.TestCase):
    def test_radio_option_value_and_selection_are_independent(self):
        suite = existence_suite(radio_design(), "register")
        self.assertNotIn('toHaveValue("")', suite)
        self.assertEqual(suite.count('toHaveValue("Male")'), 3)
        self.assertEqual(suite.count('toHaveValue("Female")'), 3)
        self.assertEqual(suite.count(".not.toBeChecked()"), 4)
        self.assertEqual(suite.count(").toBeChecked()"), 2)

    def test_missing_binding_and_radio_option_rejected(self):
        for change in (
            lambda d: d["bindings"].clear(),
            lambda d: d["elements"]["male"]["prop"].pop("value"),
        ):
            design = radio_design()
            change(design)
            with self.assertRaises(ValueError):
                validate_ui_controls(design)

    def test_contradictory_stringified_assertions_are_rejected(self):
        for source in (
            'assert.equal("expired", JSON.stringify(response.body))',
            "assert.strictEqual(JSON.stringify(body), 'Invalid input')",
            "function header(v) { return JSON.stringify(v ?? {}); } assert.ok(!header(value))",
        ):
            with self.assertRaises(ValueError):
                validate_backend_test(source)
        validate_backend_test("assert.equal(JSON.stringify(body), '{\"ok\":true}')")
        validate_backend_test('assert.equal(body.error, "expired")')

    def test_e2e_cannot_write_presentation_fixture(self):
        for source in (
            "window.__ARC_UI_FIXTURE__ = data",
            'window["__ARC_UI_FIXTURE__"] = data',
        ):
            with self.assertRaises(ValueError):
                validate_e2e_test(source)
        validate_e2e_test('await page.getByRole("button").click()')


class FrozenTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.relative = "frontend/tests/e2e/register.spec.ts"
        self.path = self.root / self.relative
        self.path.parent.mkdir(parents=True)
        self.path.write_text("original assertions")

    def test_even_explicitly_writable_test_cannot_be_edited(self):
        workspace = FileWorkspace(self.root, [self.relative])
        freeze_tests(self.root, [self.relative])
        self.assertFalse(workspace.state()[self.relative]["writable"])
        with self.assertRaisesRegex(ValueError, "Frozen test"):
            workspace.apply(
                {"edits": [{"path": self.relative, "content": "weaker assertions"}]}
            )
        self.assertEqual(self.path.read_text(), "original assertions")

    def test_modification_deletion_and_receipt_forgery_are_detected(self):
        freeze_tests(self.root, [self.relative])
        self.path.write_text("changed")
        with self.assertRaises(FrozenTestViolation):
            verify_frozen_tests(self.root)
        self.path.unlink()
        with self.assertRaises(FrozenTestViolation):
            verify_frozen_tests(self.root)
        self.path.write_text("original assertions")
        (self.root / ".arc/frozen_tests.json").write_text(json.dumps({}))
        with self.assertRaises(FrozenTestViolation):
            verify_frozen_tests(self.root)

    def test_failed_task_seal_is_archived_and_prior_suite_remains_frozen(self):
        freeze_tests(self.root, [self.relative])
        entry = {"status": "IMPLEMENTING"}
        new = "backend/tests/new.test.ts"
        with implementation_task(self.root, entry, Mock(), "new API"):
            target = self.root / new
            target.parent.mkdir(parents=True)
            target.write_text("failing new task assertions")
            freeze_tests(self.root, [new])
            raise ValueError("implementation exhausted")
        self.assertEqual(entry["status"], "FAILED")
        self.assertFalse((self.root / new).exists())
        archive = self.root / entry["archive"]
        self.assertEqual(
            (archive / "files" / new).read_text(), "failing new task assertions"
        )
        self.assertIn(new, json.loads((archive / "frozen_tests.json").read_text()))
        verify_frozen_tests(self.root)
        self.path.write_text("changed prior suite")
        with self.assertRaises(FrozenTestViolation):
            verify_frozen_tests(self.root)

    def test_non_test_and_symlink_paths_cannot_be_sealed(self):
        for path in ("frontend/src/register.ts", "../frontend/tests/register.spec.ts"):
            with self.assertRaises(FrozenTestViolation):
                freeze_tests(self.root, [path])
        linked = self.path.with_name("linked.spec.ts")
        linked.symlink_to(self.path)
        with self.assertRaises(FrozenTestViolation):
            freeze_tests(self.root, [linked.relative_to(self.root).as_posix()])
