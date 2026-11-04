"""Source-derived controls and unsupported kinds must fail before implementation."""

from copy import deepcopy
import unittest

from infrastructure.shared.agent.admission import validate_ui_controls
from infrastructure.stages.frontend.ui.contracts import (
    control_contract,
    validate_control_contract,
)
from infrastructure.stages.frontend.ui.testing import existence_suite
from test_round_one import radio_design


class ControlContractTests(unittest.TestCase):
    def test_radio_alias_is_normalized_and_covered(self):
        design = radio_design()
        for name in ("male", "female"):
            design["elements"][name]["type"] = "radio"
            design["elements"][name]["prop"].pop("input_type")
        suite = existence_suite(design, "register")
        self.assertEqual(suite.count('toHaveValue("Male")'), 3)
        self.assertEqual(design["elements"]["male"]["type"], "input")

    def test_unknown_type_and_undefined_parent_do_not_vanish(self):
        design = radio_design()
        design["elements"]["male"]["type"] = "fancy-radio"
        with self.assertRaisesRegex(ValueError, "unsupported UI type"):
            validate_ui_controls(design)
        design = radio_design()
        design["elements"]["male"]["parent"] = "missing"
        with self.assertRaisesRegex(ValueError, "missing UI parent"):
            validate_ui_controls(design)

    def test_contract_comes_from_requirement_and_rejects_decorated_name(self):
        contract = control_contract(
            {
                "id": "X",
                "description": "The example page /register contains Country fields. Country includes Sampleland.",
            }
        )
        design = radio_design()
        design["elements"]["country"] = {
            "type": "select",
            "parent": "page",
            "data": [],
            "prop": {"label": "Country", "options": ["Sampleland"]},
        }
        validate_control_contract(design, contract)
        bad = deepcopy(design)
        bad["elements"]["country"]["prop"]["label"] = "*Country:"
        with self.assertRaisesRegex(ValueError, "Country"):
            validate_control_contract(bad, contract)
        design["control_contracts"] = {"X": contract}
        suite = existence_suite(design, "register")
        self.assertIn('getByRole("combobox", { name: "Country", exact: true })', suite)

    def test_contract_rejects_missing_controls_and_wrong_options(self):
        contract = control_contract(
            {
                "id": "X",
                "description": "The example page /register contains Choice fields. Choice offers Male and Female.",
            }
        )
        design = radio_design()
        validate_control_contract(design, contract)
        design["elements"]["female"]["prop"]["value"] = "Male"
        with self.assertRaisesRegex(ValueError, "Female"):
            validate_control_contract(design, contract)

    def test_unrecognized_prose_has_explicit_limited_coverage(self):
        contract = control_contract({"id": "X", "description": "A drawing canvas."})
        self.assertEqual(contract["controls"], [])
        self.assertIn("only", contract["coverage"])


class RadioGroupContractTests(unittest.TestCase):
    def test_named_group_and_options_are_derived_from_requirement(self):
        from infrastructure.stages.frontend.ui.contracts import radio_group_suite

        contract = control_contract(
            {
                "id": "R",
                "description": "The example page /register contains Choice fields. Choice offers Male and Female.",
            }
        )
        self.assertEqual(contract["radio_groups"][0]["name"], "Choice")
        suite = radio_group_suite([contract])
        self.assertIn('getByRole("radiogroup", { name: "Choice", exact: true })', suite)
        self.assertIn('.getByRole("radio", { name: "Male", exact: true })', suite)
        self.assertIn('.getByRole("radio", { name: "Female", exact: true })', suite)
