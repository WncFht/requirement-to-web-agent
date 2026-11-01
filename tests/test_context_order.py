"""Ordering can extend a shared prefix without removing context or changing permissions."""

import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from infrastructure.shared.agent.files import FileWorkspace
from infrastructure.shared.models.context_order import (
    stable_first,
    stable_creation_first,
)


class ContextOrderTests(unittest.TestCase):
    def test_refined_order_is_opt_in_and_changes_no_values(self):
        value = {
            "event_id": "e",
            "event": {"x": 1},
            "frontend_data": {"x": ""},
            "page_inventory": {},
            "all_requirement_uses": ["same"],
            "backend_apis": {},
        }
        with patch.dict(
            os.environ, {"ARC_CACHE_PREFIX": "1", "ARC_CACHE_PREFIX_V2": "1"}
        ):
            result = stable_first(value, ("frontend_data", "page_inventory"))
            self.assertEqual(
                list(result)[:4],
                [
                    "frontend_data",
                    "page_inventory",
                    "all_requirement_uses",
                    "backend_apis",
                ],
            )
            self.assertEqual(result, value)
            creation = {
                "creation_scope": "target",
                "requirement": {},
                "page_inventory": {},
                "source_elements": {"target": True},
                "frontend_data": {"shared": 1},
                "page_paths": {"home": "home.tsx"},
            }
            ordered = stable_creation_first(creation)
            self.assertEqual(creation, ordered)
            self.assertLess(
                list(ordered).index("frontend_data"),
                list(ordered).index("source_elements"),
            )
        with patch.dict(
            os.environ, {"ARC_CACHE_PREFIX": "1", "ARC_CACHE_PREFIX_V2": "0"}
        ):
            self.assertIs(stable_creation_first(creation), creation)
        with patch.dict(
            os.environ, {"ARC_CACHE_PREFIX": "0", "ARC_CACHE_PREFIX_V2": "1"}
        ):
            self.assertIs(stable_first(value, ("frontend_data",)), value)
            self.assertIs(stable_creation_first(creation), creation)

    def test_stable_fields_move_first_with_identical_values_and_keys(self):
        request = {
            "event_id": "EV-input",
            "event": {"read": ["input"]},
            "frontend_data": {"input": ""},
            "page_inventory": ["home"],
            "backend_apis": {},
        }
        with patch.dict(os.environ, {"ARC_CACHE_PREFIX": "1"}):
            ordered = stable_first(request, ("frontend_data", "page_inventory"))
        self.assertEqual(ordered, request)
        self.assertEqual(list(ordered)[:2], ["frontend_data", "page_inventory"])
        self.assertIs(ordered["event"], request["event"])
        with patch.dict(os.environ, {"ARC_CACHE_PREFIX": "0"}):
            self.assertIs(stable_first(request, ("frontend_data",)), request)

    def test_page_changes_preserve_longer_prefix_and_exact_edit_scope(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            page = "frontend/src/pages/Home.tsx"
            references = [
                "frontend/src/ui-events.ts",
                "frontend/src/ui-api.ts",
                "frontend/src/ui-runtime.ts",
            ]
            for relative in [page, *references]:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("original-page" if relative == page else relative * 30)
            prefixes, states = {}, {}
            for flag in ("0", "1"):
                (root / page).write_text("original-page")
                with patch.dict(os.environ, {"ARC_CACHE_PREFIX": flag}):
                    workspace = FileWorkspace(root, {page}, references)
                before = workspace.state()
                (root / page).write_text("changed-page")
                after = workspace.state()
                left, right = json.dumps(before), json.dumps(after)
                prefixes[flag] = next(
                    (
                        index
                        for index, pair in enumerate(zip(left, right))
                        if pair[0] != pair[1]
                    ),
                    min(len(left), len(right)),
                )
                states[flag] = (before, after)
                self.assertTrue(after[page]["writable"])
                self.assertTrue(all(not after[name]["writable"] for name in references))
                with self.assertRaises(ValueError):
                    workspace.apply(
                        {"edits": [{"path": references[0], "content": "forbidden"}]}
                    )
            self.assertEqual(states["0"], states["1"])
            self.assertGreater(prefixes["1"], prefixes["0"] + 1000)
