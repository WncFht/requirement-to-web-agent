"""Single-event creation retains business evidence and avoids unrelated file payloads."""

from copy import deepcopy
import unittest

from infrastructure.stages.frontend.interactions.creation_context import (
    creation_context,
)


class CreationContextTests(unittest.TestCase):
    def context(self):
        return {
            "requirement": {
                "id": "R",
                "description": "exact identity",
                "steps": ["success", "rejection"],
                "reference_tests": {"x.ts": "frozen original"},
            },
            "page_subtrees": {
                "home": {
                    "name": "Home",
                    "route": "/",
                    "root": "root",
                    "elements": {
                        "button": {"data": ["input"], "prop": {"label": "Submit"}},
                        "other": {},
                    },
                    "bindings": {
                        "input": {"initial": ""},
                        "read_only": {"initial": "required for transformation"},
                    },
                }
            },
            "triggers": {
                "one": {"source": "button", "event": "click", "action": "target"},
                "two": {"source": "root", "event": "mount", "action": "target"},
                "other": {"source": "other", "event": "click", "action": "unrelated"},
            },
            "events": {
                "target": {
                    "write": ["input"],
                    "actions": [
                        {"kind": "api", "api": "A"},
                        {"kind": "navigate", "page": "home"},
                    ],
                },
                "unrelated": {"actions": []},
            },
            "contracts": {
                "target": {
                    "precondition": ["valid"],
                    "postcondition": ["failure preserves records"],
                },
                "unrelated": {},
            },
            "backend_apis": {"A": {"response": {"errors": [409]}}, "B": {}},
        }

    def test_complete_target_and_all_shared_triggers_survive(self):
        context = self.context()
        original = deepcopy(context)
        task = creation_context(
            context, "target", {"target": None}, {"home": "home.tsx"}
        )
        self.assertEqual(task["events"], {"target": context["events"]["target"]})
        self.assertEqual(set(task["triggers"]), {"one", "two"})
        self.assertEqual(task["contracts"]["target"], context["contracts"]["target"])
        self.assertEqual(task["backend_apis"], {"A": context["backend_apis"]["A"]})
        self.assertIn("read_only", task["frontend_data"])
        self.assertNotIn("reference_tests", task["requirement"])
        self.assertEqual(task["requirement"]["steps"], ["success", "rejection"])
        task["events"]["target"]["write"].append("changed")
        self.assertEqual(context, original)

    def test_missing_contract_fails_instead_of_silently_dropping_it(self):
        context = self.context()
        del context["contracts"]["target"]
        with self.assertRaises(KeyError):
            creation_context(context, "target", {"target": None}, {})
