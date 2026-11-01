"""IR radio ownership must be observable through the real semantic group."""

import os
import unittest
from unittest.mock import patch

from test_frontend_flow import frontend_fixture, node, binding
from infrastructure.stages.frontend.ui.testing import existence_suite
from infrastructure.stages.frontend.ui.label_contracts import radio_group_instructions


class RadioContainmentTests(unittest.TestCase):
    def fixture(self):
        design = frontend_fixture()[2]
        design["bindings"]["gender"] = binding("string", "Male", "Selection")
        design["elements"]["UI-GENDER"] = node(
            "container", "UI-FORM", [], role="radiogroup", label="Gender"
        )
        design["elements"]["UI-MALE"] = node(
            "input",
            "UI-GENDER",
            ["gender"],
            input_type="radio",
            label="Male",
            value="Male",
        )
        design["elements"]["UI-FEMALE"] = node(
            "input",
            "UI-GENDER",
            ["gender"],
            input_type="radio",
            label="Female",
            value="Female",
        )
        return design

    def test_roles_and_labels_resolve_actual_radios_inside_their_group(self):
        with patch.dict(os.environ, {"ARC_LEGACY_RADIO_CONTAINMENT": "0"}):
            suite = existence_suite(self.fixture(), "editor")
        self.assertIn(
            'getByRole("radiogroup", { name: "Gender", exact: true })).toHaveAttribute("data-testid", "UI-GENDER")',
            suite,
        )
        self.assertIn(
            'getByTestId("UI-GENDER").getByRole("radio", { name: "Male", exact: true })).toHaveAttribute("data-testid", "UI-MALE")',
            suite,
        )
        self.assertIn(
            'getByTestId("UI-GENDER").getByRole("radio", { name: "Female", exact: true })).toHaveAttribute("data-testid", "UI-FEMALE")',
            suite,
        )

    def test_extra_layout_layer_preserves_semantic_ownership(self):
        design = self.fixture()
        design["elements"]["UI-LAYOUT"] = node("container", "UI-GENDER", [])
        design["elements"]["UI-MALE"]["parent"] = "UI-LAYOUT"
        suite = existence_suite(design, "editor")
        self.assertIn(
            'getByTestId("UI-GENDER").getByRole("radio", { name: "Male", exact: true })',
            suite,
        )

    def test_rollback_keeps_the_original_radio_and_label_checks(self):
        with patch.dict(os.environ, {"ARC_LEGACY_RADIO_CONTAINMENT": "1"}):
            suite = existence_suite(self.fixture(), "editor")
            self.assertEqual(radio_group_instructions(), "")
        self.assertNotIn('getByRole("radiogroup"', suite)
        self.assertIn('getByTestId("UI-MALE")).toHaveValue("Male")', suite)
        self.assertIn('getByTestId("UI-MALE")).toBeChecked()', suite)
