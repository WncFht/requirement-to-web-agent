"""A designed signed-in fixture must display the username required by supplied tests."""

from copy import deepcopy
import os
import unittest
from unittest.mock import patch

from test_frontend_flow import frontend_fixture, binding, node
from infrastructure.stages.frontend.context import validate_reference_controls


class IdentityDisplayTests(unittest.TestCase):
    def fixture(self):
        design = deepcopy(frontend_fixture()[2])
        design["pages"]["editor"]["route"] = "/"
        design["bindings"]["display.username"] = binding(
            "string", "", "Resolved username"
        )
        design["pages"]["editor"]["fixtures"]["signedIn"] = {
            "display.username": "taken_traveler"
        }
        context = {
            "reference_tests": {
                "helpers.ts": "await expect(page.getByText(account.username, { exact: true })).toBeVisible();"
            }
        }
        return design, context

    def test_missing_identity_display_is_rejected_but_bound_text_is_accepted(self):
        design, context = self.fixture()
        with self.assertRaisesRegex(ValueError, "no text"):
            validate_reference_controls(design, context)
        design["elements"]["UI-IDENTITY"] = node(
            "text", "UI-FORM", ["display.username"]
        )
        validate_reference_controls(design, context)

    def test_check_requires_external_contract_and_supports_rollback(self):
        design, context = self.fixture()
        validate_reference_controls(design, {})
        with patch.dict(os.environ, {"ARC_LEGACY_IDENTITY_DISPLAY": "1"}):
            validate_reference_controls(design, context)
