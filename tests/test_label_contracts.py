"""The browser gate must match a label to the actual control, not a wrapper."""

from copy import deepcopy
import unittest

from test_frontend_flow import frontend_fixture, node, binding
from infrastructure.stages.frontend.ui.testing import existence_suite


class LabelContractTests(unittest.TestCase):
    def fixture(self):
        design = deepcopy(frontend_fixture()[2])
        design["bindings"]["password"] = binding("string", "", "Transient password")
        design["elements"]["UI-PASSWORD"] = node(
            "input", "UI-FORM", ["password"], input_type="password", label="Password"
        )
        return design

    def test_password_label_resolves_to_the_actual_input(self):
        suite = existence_suite(self.fixture(), "editor")
        self.assertIn(
            'getByTestId("UI-EDITOR").getByLabel("Password", { exact: true })).toHaveAttribute("data-testid", "UI-PASSWORD")',
            suite,
        )
        self.assertIn(
            'getByTestId("UI-PASSWORD")).toHaveAttribute("type", "password")', suite
        )
        self.assertIn(
            'getByTestId("UI-PASSWORD")).toHaveAccessibleName("Password")', suite
        )
