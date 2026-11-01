"""Frontend representation, publication, lifecycle dependencies and acceptance regressions."""

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

from infrastructure.stages.requirements.tree import RequirementTree
from infrastructure.stages.frontend.context import (
    load_ui_context,
    reference_tests,
    validate_reference_controls,
)
from infrastructure.stages.frontend.ui.design import (
    apply_proposal,
    empty_design,
    page_context,
    validate_design,
)
from infrastructure.stages.frontend.ui.synthesis import synthesize_ui
from infrastructure.stages.frontend.ui.testing import (
    presentation_run_status,
    existence_suite,
)
from infrastructure.stages.frontend.interactions.contracts import validate_contract
from infrastructure.stages.frontend.interactions.design import (
    empty_interactions,
    validate_interactions,
)
from infrastructure.stages.frontend.interactions.synthesis import propose
from infrastructure.stages.frontend.interactions.implementation import (
    scenario_context,
    test_run_status,
)
from infrastructure.utils.files import save_json, save_text


def node(kind, parent, data=(), mode=(), **props):
    return {
        "type": kind,
        "parent": parent,
        "data": list(data),
        "mode": list(mode),
        "prop": props,
    }


def binding(dtype, initial, source):
    return {"dtype": dtype, "constraints": [], "initial": initial, "source": source}


def frontend_fixture():
    """A shared editor navigates to a later requirement's read-only summary page."""
    raw = {
        "id": "ROOT",
        "name": "Notes",
        "children": [
            {
                "id": rid,
                "name": rid,
                "description": description,
                "scenarios": [
                    {
                        "id": "SCN-" + rid,
                        "steps": [
                            {
                                "id": "STEP-" + rid,
                                "Given": "Existing notes in the database",
                                "When": behavior,
                                "Then": outcome,
                            }
                        ],
                    }
                ],
            }
            for rid, description, behavior, outcome in (
                (
                    "REQ-A",
                    "Save a note then navigate to /summary; empty text is rejected without writes.",
                    "Enter text and submit the editor",
                    "Show the updated count after navigation and refresh; show an error on rejection",
                ),
                (
                    "REQ-B",
                    "Use the same editor and API to save another note.",
                    "Enter another note and save",
                    "Persist it and display the summary",
                ),
                (
                    "REQ-C",
                    "The /summary page displays the count on every entry and refresh without writes.",
                    "Open or refresh /summary",
                    "Display the persisted count and allow returning to the editor",
                ),
            )
        ],
    }
    tree = RequirementTree(raw)
    ui = {
        "pages": {
            "editor": {
                "name": "Editor",
                "route": "/",
                "root": "UI-EDITOR",
                "images": [],
                "fixtures": {
                    "default": {},
                    "rejected": {
                        "form.errorVisible": True,
                        "form.error": "Text required",
                    },
                },
            },
            "summary": {
                "name": "Summary",
                "route": "/summary",
                "root": "UI-SUMMARY",
                "images": [],
                "fixtures": {"default": {}, "loaded": {"summary.count": "2"}},
            },
        },
        "elements": {
            "UI-EDITOR": node("page", None),
            "UI-FORM": node("form", "UI-EDITOR"),
            "UI-TEXT": node(
                "input",
                "UI-FORM",
                ["form.text"],
                ["user_write"],
                label="Note",
                input_type="text",
            ),
            "UI-SAVE": node("button", "UI-FORM", text="Save"),
            "UI-ERROR": node(
                "alert",
                "UI-EDITOR",
                ["form.error"],
                visible={"var": "form.errorVisible", "equals": True},
            ),
            "UI-SUMMARY": node("page", None),
            "UI-COUNT": node("text", "UI-SUMMARY", ["summary.count"]),
            "UI-BACK": node("link", "UI-SUMMARY", text="Back", href="/"),
        },
        "bindings": {
            "form.text": binding("string", "", "Native note input"),
            "form.error": binding("string", "", "API rejection message"),
            "form.errorVisible": binding("boolean", False, "Whether to show rejection"),
            "summary.count": binding("string", "Loading", "Count API response"),
        },
        "requirements": {
            "ROOT": [],
            "REQ-A": ["UI-EDITOR", "UI-FORM", "UI-TEXT", "UI-SAVE", "UI-ERROR"],
            "REQ-B": ["UI-EDITOR", "UI-FORM", "UI-TEXT", "UI-SAVE", "UI-ERROR"],
            "REQ-C": ["UI-SUMMARY", "UI-COUNT", "UI-BACK"],
        },
        "steps": {
            "STEP-REQ-A": ["UI-TEXT", "UI-SAVE", "UI-ERROR"],
            "STEP-REQ-B": ["UI-TEXT", "UI-SAVE"],
            "STEP-REQ-C": ["UI-COUNT", "UI-BACK"],
        },
    }
    interactions = {
        "triggers": {
            "TR-INPUT": {"source": "UI-TEXT", "event": "change", "action": "EV-INPUT"},
            "TR-SAVE": {"source": "UI-FORM", "event": "submit", "action": "EV-SAVE"},
            "TR-COUNT": {
                "source": "UI-SUMMARY",
                "event": "mount",
                "action": "EV-COUNT",
            },
        },
        "events": {
            "EV-INPUT": {
                "description": "Remember native text",
                "write": ["form.text"],
                "actions": [
                    {
                        "id": "SET-TEXT",
                        "kind": "local",
                        "description": "Write input.value into form.text",
                    }
                ],
            },
            "EV-SAVE": {
                "description": "Save or show the rejection",
                "write": ["form.error", "form.errorVisible"],
                "actions": [
                    {
                        "id": "SAVE",
                        "kind": "api",
                        "api": "API-SAVE",
                        "description": "POST form.text as body.text",
                    },
                    {
                        "id": "ERROR",
                        "kind": "local",
                        "description": "On SAVE status 400 show its error message and set form.errorVisible=true",
                    },
                    {
                        "id": "OPEN-SUMMARY",
                        "kind": "navigate",
                        "page": "summary",
                        "description": "On SAVE status 200 navigate to summary",
                    },
                ],
            },
            "EV-COUNT": {
                "description": "Load persisted count on entry",
                "write": ["summary.count"],
                "actions": [
                    {
                        "id": "COUNT",
                        "kind": "api",
                        "api": "API-COUNT",
                        "description": "GET the current count",
                    },
                    {
                        "id": "SHOW-COUNT",
                        "kind": "local",
                        "description": "Write String(COUNT response.body.count) to summary.count",
                    },
                ],
            },
        },
        "contracts": {
            "EV-INPUT": {
                "precondition": [],
                "postcondition": ["The current native text is available to submit."],
            },
            "EV-SAVE": {
                "precondition": [],
                "postcondition": [
                    "A successful save persists one note and opens summary.",
                    "A 400 response displays the error and performs no write.",
                ],
            },
            "EV-COUNT": {
                "precondition": [],
                "postcondition": [
                    "Show the count on entry and refresh; leave the database unchanged."
                ],
            },
        },
        "requirements": {
            "ROOT": [],
            "REQ-A": ["TR-INPUT", "TR-SAVE"],
            "REQ-B": ["TR-INPUT", "TR-SAVE"],
            "REQ-C": ["TR-COUNT"],
        },
        "steps": {
            "STEP-REQ-A": ["TR-INPUT", "TR-SAVE"],
            "STEP-REQ-B": ["TR-INPUT", "TR-SAVE"],
            "STEP-REQ-C": ["TR-COUNT"],
        },
    }
    backend = {
        "requirements": {
            "ROOT": [],
            "REQ-A": ["API-SAVE"],
            "REQ-B": ["API-SAVE"],
            "REQ-C": ["API-COUNT"],
        },
        "apis": {
            "API-SAVE": {"read": [], "write": ["Note.id", "Note.text"]},
            "API-COUNT": {"read": ["Note.id", "Note.text"], "write": []},
        },
    }
    obligations = {
        "requirements": {
            rid: {
                "read": [] if rid != "REQ-C" else ["Note.id", "Note.text"],
                "write": ["Note.id", "Note.text"] if rid in {"REQ-A", "REQ-B"} else [],
            }
            for rid in tree.requirements
        }
    }
    return raw, tree, ui, interactions, backend, obligations


class FrontendFlow(unittest.TestCase):
    def setUp(self):
        (
            self.raw,
            self.tree,
            self.ui,
            self.interactions,
            self.backend,
            self.obligations,
        ) = frontend_fixture()
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.output = Path(temporary.name)
        self.arc = self.output / ".arc"

    def test_ui_checks_only_json_shape(self):
        ui = deepcopy(self.ui)
        ui["elements"]["UI-SAVE"]["mode"] = ["user_write"]
        ui["elements"]["UI-SAVE"]["data"] = ["form.submitting"]
        ui["bindings"]["form.submitting"] = binding("boolean", "not type checked", "")
        ui["bindings"]["form.submitting"]["owner"] = "any node"
        ui["pages"]["summary"]["route"] = "/"
        validate_design(ui, self.tree, {}, complete=True)
        state = deepcopy(self.interactions)
        validate_interactions(
            state,
            ui,
            self.tree,
            {},
            self.obligations,
            self.backend,
            self.tree.leaves,
            complete=True,
        )
        ui["elements"]["UI-SAVE"]["data"] = 123
        with self.assertRaisesRegex(ValueError, "JSON shape"):
            validate_design(ui, self.tree, {})

    def test_multiple_new_events_keep_model_paths_and_run_complete_acceptance(self):
        from unittest.mock import patch
        from infrastructure.shared.agent.files import FileWorkspace
        from infrastructure.shared.project.entrypoints import selected_path
        from infrastructure.shared.project.initialize import initialize_project
        from infrastructure.stages.frontend.interactions import implementation

        initialize_project(self.output)
        for pid in self.ui["pages"]:
            workspace = FileWorkspace.for_target(self.output, "page", pid)
            workspace.state()
            workspace.apply(
                {
                    "edits": [
                        {
                            "path": f"frontend/src/screens/{pid}.tsx",
                            "content": "export function Page() {return null;}",
                        }
                    ]
                }
            )
        calls = []

        def generate(instructions, payload):
            task = payload["task"]
            creation = task["new_file"]
            if creation["kind"] == "e2e_test":
                self.assertTrue(
                    payload["files"]["frontend/src/screens/editor.tsx"]["writable"]
                )
                self.assertFalse(
                    payload["files"]["frontend/src/ui-runtime.ts"]["writable"]
                )
            calls.append(deepcopy(task))
            suffix = ".spec.ts" if creation["kind"] == "e2e_test" else ".ts"
            path = f"{creation['directory']}/chosen/{creation['target']}{suffix}"
            return {"edits": [{"path": path, "content": "export function handle() {}"}]}

        checks, ui_checks = Mock(), Mock()
        checks.typecheck.return_value = {"returncode": 0, "output": "compiled"}
        checks.build.return_value = {"returncode": 0, "output": "built"}
        green = {
            "returncode": 0,
            "output": "passed",
            "passed": 1,
            "failed": 0,
            "skipped": 0,
            "flaky": 0,
            "errors": [],
            "failures": [],
        }
        ui_checks.tests.return_value = green

        def test_events(files, **kwargs):
            if all(
                selected_path(self.output, "event", eid)
                for eid in self.interactions["events"]
            ):
                return green
            return {
                **green,
                "returncode": 1,
                "passed": 0,
                "failed": 1,
                "failures": ["expect(received).toBe(expected)"],
            }

        checks.tests.side_effect = test_events
        backend = deepcopy(self.backend)
        for aid, api in backend["apis"].items():
            api["signature"] = {"method": "POST", "path": "/api/" + aid, "name": aid}
        with (
            patch.object(implementation, "install_dependencies"),
            patch.object(implementation, "E2EChecks", return_value=checks),
            patch.object(implementation, "FrontendChecks", return_value=ui_checks),
            patch.object(
                implementation,
                "observe_cookie_transport",
                return_value={"status": "OBSERVED", "names": ["session_id"]},
            ),
        ):
            report = implementation.run_interaction_tdd(
                self.arc,
                self.tree,
                {"entities": {}},
                backend,
                self.ui,
                self.interactions,
                {},
                {rid: {"id": rid} for rid in self.tree.leaves},
                Mock(generate_json=generate),
                Mock(),
                {"requirements": {}},
                max_turns=2,
            )
        self.assertEqual(report["status"], "GREEN")
        creations = [
            task["new_file"]["target"]
            for task in calls
            if task["new_file"]["kind"] == "event"
        ]
        self.assertEqual(creations, ["EV-COUNT", "EV-INPUT", "EV-SAVE"])
        self.assertEqual(report["requirements"]["REQ-A"]["implementation_turns"], 3)
        self.assertEqual(report["requirements"]["REQ-B"]["implementation_turns"], 0)
        self.assertIn(
            "chosen/REQ-A.spec.ts", report["requirements"]["REQ-A"]["test_path"]
        )
        self.assertGreater(checks.tests.call_count, 3)

    def test_runtime_types_survive_returning_to_presentation_stage(self):
        from infrastructure.shared.project.initialize import initialize_project
        from infrastructure.stages.frontend.ui.runtime import prepare_frontend
        from infrastructure.stages.frontend.interactions.runtime import (
            sync_interactions,
        )
        from infrastructure.utils.files import read_source

        initialize_project(self.output)
        sync_interactions(
            self.output,
            {"pages": {}, "bindings": {}},
            {"events": {}, "triggers": {}},
            {"apis": {}},
            [],
        )
        before = read_source(self.output / "frontend/src/ui-runtime.ts")
        prepare_frontend(self.output)
        after = read_source(self.output / "frontend/src/ui-runtime.ts")
        self.assertEqual(before, after)
        self.assertIn("export interface UiEventContext", after)
        self.assertEqual(after.count("export type UiEventHandler"), 1)

    def test_synthesis_retries_without_publishing_rejected_state(self):
        requests = []

        def generate(instructions, payload):
            requests.append(deepcopy(payload))
            rid = payload["requirement"]["id"]
            page = "summary" if rid == "REQ-C" else "editor"
            context = page_context(self.ui, page)
            proposal = {
                "pages": {page: self.ui["pages"][page]} if rid != "REQ-B" else {},
                "elements": context["elements"] if rid != "REQ-B" else {},
                "bindings": context["bindings"] if rid != "REQ-B" else {},
                "requirement_ui": self.ui["requirements"][rid],
                "step_ui": {
                    sid: self.ui["steps"][sid] for sid in self.tree.own_steps[rid]
                },
            }
            if len(requests) == 1:
                proposal = deepcopy(proposal)
                proposal["bindings"]["form.text"]["source"] = 7
            return proposal

        contexts = {
            rid: {
                **record,
                "steps": [self.tree.steps[sid] for sid in self.tree.own_steps[rid]],
                "images": {},
            }
            for rid, record in self.tree.requirements.items()
        }
        result = synthesize_ui(
            self.arc,
            self.tree,
            {"entities": {}},
            self.backend,
            {},
            contexts,
            Mock(generate_json=generate),
            Mock(),
        )
        self.assertEqual(result, self.ui)
        self.assertEqual(len(requests), 4)
        self.assertIn("correction", requests[1])
        self.assertEqual(requests[1]["retrieved_pages"], {})
        self.assertNotIn("step_obligations", requests[0])

    def test_presentation_loader_has_no_report_policy(self):
        save_json(self.arc / "requirements.json", self.raw)
        save_json(self.arc / "visual_analysis.json", {})
        tree, images, contexts = load_ui_context(self.arc, self.output)
        self.assertEqual(tree.leaves, self.tree.leaves)
        self.assertEqual(images, {})
        self.assertNotIn("concatenated_steps", contexts["REQ-A"])

    def test_external_radio_group_cannot_be_replaced_by_select(self):
        ui = {"elements": {"gender": node("select", None, label="Gender")}}
        context = {
            "reference_tests": {
                "helpers.ts": "page.getByRole('radiogroup', { name: 'Gender', exact: true })"
            }
        }
        with self.assertRaisesRegex(ValueError, "radiogroup"):
            validate_reference_controls(ui, context)
        ui["elements"]["gender"] = node(
            "container", None, label="Gender", role="radiogroup"
        )
        validate_reference_controls(ui, context)

    def test_interaction_retry_explains_that_rejected_records_are_not_accepted(self):
        accepted = {"triggers": {}, "events": {"old": {"description": "accepted"}}}
        request = {"existing_interactions": deepcopy(accepted)}
        model = Mock()
        model.generate_json.side_effect = [{"rejected": True}, {"complete": True}]
        validator = Mock(side_effect=[ValueError("excess reads"), "accepted result"])
        result, response = propose(
            model, "instructions", request, validator, Mock(), "test"
        )
        self.assertEqual(result, "accepted result")
        self.assertEqual(response, {"complete": True})
        self.assertEqual(request["existing_interactions"], accepted)
        self.assertIn("NOT applied", request["correction"]["retry_base"])
        self.assertEqual(
            request["correction"]["trigger_record_example"]["TR-example"]["event"],
            "mount",
        )

    def test_radio_presence_distinguishes_option_value_and_shared_selection(self):
        ui = deepcopy(self.ui)
        ui["bindings"]["gender"] = binding("string", "Male", "Selected option")
        for option in ["Male", "Female"]:
            ui["elements"]["radio-" + option] = node(
                "input",
                "UI-FORM",
                ["gender"],
                input_type="radio",
                value=option,
                label=option,
            )
        suite = existence_suite(ui, "editor")
        self.assertIn('getByTestId("radio-Female")).toHaveValue("Female")', suite)
        self.assertIn('getByTestId("radio-Female")).not.toBeChecked()', suite)
        self.assertIn('getByTestId("radio-Male")).toBeChecked()', suite)
        with patch.dict("os.environ", {"ARC_LEGACY_RADIO_ASSERTIONS": "1"}):
            legacy = existence_suite(ui, "editor")
            self.assertIn('getByTestId("radio-Female")).toHaveValue("Male")', legacy)

    def test_radio_design_requires_its_static_option_value(self):
        with self.assertRaisesRegex(ValueError, "prop.value"):
            validate_reference_controls(
                {"elements": {"x": node("input", None, input_type="radio")}}, {}
            )

    def test_supplied_reference_tests_remain_exact_and_can_be_disabled(self):
        tests = self.output / "tests"
        tests.mkdir()
        content = "// Historical ID; exact accessible contract\n"
        (tests / "REQ-old.spec.ts").write_text(content)
        self.assertEqual(
            reference_tests(self.output), {"tests/REQ-old.spec.ts": content}
        )
        with patch.dict("os.environ", {"ARC_LEGACY_REFERENCE_TESTS": "1"}):
            self.assertEqual(reference_tests(self.output), {})

    def test_reference_tests_are_available_without_filename_requirement_mapping(self):
        save_json(self.arc / "requirements.json", self.raw)
        save_json(self.arc / "visual_analysis.json", {})
        (self.output / "tests").mkdir()
        save_text(self.output / "tests/old-id.spec.ts", "external contract")
        _, _, contexts = load_ui_context(self.arc, self.output)
        for context in contexts.values():
            self.assertEqual(
                context["reference_tests"],
                {"tests/old-id.spec.ts": "external contract"},
            )

    def test_frontend_calls_are_checked_by_database_fields(self):
        validate_interactions(
            self.interactions,
            self.ui,
            self.tree,
            {},
            self.obligations,
            self.backend,
            self.tree.leaves,
            complete=True,
        )
        state = deepcopy(self.interactions)
        state["events"]["EV-INPUT"]["write"] = []
        state["events"]["EV-SAVE"]["read"] = ["undeclared frontend state"]
        state["triggers"]["TR-DUP"] = state["triggers"]["TR-INPUT"]
        state["triggers"]["TR-SAVE"]["event"] = "anything"
        validate_interactions(
            state,
            self.ui,
            self.tree,
            {},
            self.obligations,
            self.backend,
            self.tree.leaves,
        )
        alternative = deepcopy(self.backend)
        alternative["apis"]["API-SAME-FIELDS"] = deepcopy(
            alternative["apis"]["API-SAVE"]
        )
        state["events"]["EV-SAVE"]["actions"][0]["api"] = "API-SAME-FIELDS"
        validate_interactions(
            state,
            self.ui,
            self.tree,
            {},
            self.obligations,
            alternative,
            self.tree.leaves,
        )
        state["events"]["EV-SAVE"]["actions"][0]["api"] = "API-COUNT"
        with self.assertRaisesRegex(ValueError, "Obligation"):
            validate_interactions(
                state,
                self.ui,
                self.tree,
                {},
                self.obligations,
                alternative,
                self.tree.leaves,
            )
        validate_contract(
            "EV", {"precondition": [], "postcondition": [], "actions": {}}
        )
        with self.assertRaises(ValueError):
            validate_contract("EV", {"precondition": {}, "postcondition": []})

    def test_navigation_context_includes_later_page_mount_and_keeps_ownership(self):
        context = scenario_context(self.ui, self.interactions, "REQ-A")
        self.assertEqual(set(context["page_subtrees"]), {"editor", "summary"})
        self.assertEqual(set(context["events"]), {"EV-INPUT", "EV-SAVE", "EV-COUNT"})
        self.assertEqual(len(context["triggers"]), 3)
        self.assertEqual(
            self.interactions["requirements"]["REQ-A"], ["TR-INPUT", "TR-SAVE"]
        )

    def test_backend_only_requirements_need_no_frontend_effect_coverage(self):
        ui = empty_design()
        ui["requirements"] = {rid: [] for rid in self.tree.requirements}
        ui["steps"] = {sid: [] for sid in self.tree.steps}
        validate_design(ui, self.tree, {}, complete=True)
        interactions = empty_interactions(self.tree)
        validate_interactions(
            interactions,
            ui,
            self.tree,
            {},
            self.obligations,
            self.backend,
            self.tree.leaves,
            complete=True,
        )
        self.assertEqual(scenario_context(ui, interactions, "REQ-A")["events"], {})

    def test_frontend_runtime_failure_is_repair_not_test_regeneration(self):
        report = {
            "returncode": 1,
            "failed": 1,
            "errors": [],
            "failures": ["E2E_RUNTIME_ERROR: Broken handler"],
        }
        self.assertEqual(test_run_status(report), "REPAIR_REQUIRED")
        page_report = {**report, "failures": ["UI_RUNTIME_ERROR: Broken page"]}
        self.assertEqual(presentation_run_status(page_report), "REPAIR_REQUIRED")
        report["failures"] = ["E2E_BACKEND_ERROR: undeclared response"]
        with self.assertRaises(ValueError):
            test_run_status(report)


if __name__ == "__main__":
    unittest.main()
