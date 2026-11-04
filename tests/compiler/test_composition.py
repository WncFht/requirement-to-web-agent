"""Composition may reuse generated source but must retain provenance and runtime contracts."""

from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from validate_composition import merge_page
from test_round_one import radio_design


class CompositionTests(unittest.TestCase):
    def test_replacement_isolated_and_runtime_binding_conflicts_rejected(self):
        base = radio_design()
        base.update(requirements={"R": ["page", "male", "female"]}, steps={})
        base["pages"]["other"] = {
            "root": "other",
            "route": "/other",
            "fixtures": {"default": {}},
        }
        base["elements"]["other"] = {
            "type": "page",
            "parent": None,
            "data": ["gender"],
            "prop": {},
        }
        original = deepcopy(base)
        replacement = deepcopy(base)
        replacement["bindings"]["gender"]["source"] = "Different explanatory prose"
        merged = merge_page(base, replacement, "register")
        self.assertEqual(base, original)
        self.assertEqual(merged["elements"]["other"], base["elements"]["other"])
        self.assertEqual(merged["bindings"]["gender"], base["bindings"]["gender"])
        replacement["bindings"]["gender"]["initial"] = "Male"
        with self.assertRaisesRegex(ValueError, "Shared runtime"):
            merge_page(base, replacement, "register")

    def test_foreign_element_collision_rejected(self):
        base = radio_design()
        base.update(requirements={}, steps={})
        base["elements"]["foreign"] = {
            "type": "text",
            "parent": None,
            "data": [],
            "prop": {},
        }
        replacement = deepcopy(base)
        replacement["elements"]["foreign"]["parent"] = "page"
        with self.assertRaisesRegex(ValueError, "collides"):
            merge_page(base, replacement, "register")
