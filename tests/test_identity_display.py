"""A designed signed-in fixture must display the username required by supplied tests."""

from copy import deepcopy
import unittest

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

    def test_check_requires_external_contract(self):
        design, _ = self.fixture()
        validate_reference_controls(design, {})
