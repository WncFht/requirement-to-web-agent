"""Frontend inputs retain image/page evidence alongside normalized requirements."""

import json
import os
import re

from infrastructure.stages.backend.context import load_context
from infrastructure.stages.requirements.tree import RequirementTree
from infrastructure.utils.files import read_artifact
from infrastructure.stages.backend.contracts import validate_contracts
from infrastructure.stages.backend.primitives import validate_design
from infrastructure.stages.database.obligations.records import field_symbols

REFERENCE = re.compile(r"\\ref\[image\]\(([^)]+)\)")


def reference_tests(input_dir):
    """Expose supplied interaction contracts as read-only evidence, never generated tests."""
    if os.getenv("ARC_LEGACY_REFERENCE_TESTS", "0") == "1":
        return {}
    root = input_dir.resolve()
    return {
        path.relative_to(root).as_posix(): path.read_text(encoding="utf-8-sig")
        for path in sorted((root / "tests").rglob("*.ts"))
        if path.resolve().is_relative_to(root) and path.is_file()
    }


def validate_reference_controls(design, context):
    """Reject a select where a supplied external contract requires a radio group."""
    if os.getenv("ARC_LEGACY_REFERENCE_TESTS", "0") == "1":
        return
    sources = "\n".join(context.get("reference_tests", {}).values())
    groups = set(
        re.findall(
            r"""getByRole\(\s*['"]radiogroup['"]\s*,\s*\{\s*name:\s*['"]([^'"]+)['"]""",
            sources,
        )
    )
    for uid, node in design["elements"].items():
        prop = node.get("prop", {})
        if node["type"] == "select" and prop.get("label") in groups:
            raise ValueError(
                f"External interaction contract requires radiogroup {prop['label']!r}; "
                f"{uid} is a select. Use a labeled container with prop.role=radiogroup "
                "and input children with input_type=radio, static prop.value and a shared selection binding."
            )
        if (
            node["type"] == "input"
            and prop.get("input_type") == "radio"
            and not isinstance(prop.get("value"), str)
        ):
            raise ValueError(f"Radio input {uid} needs a static string prop.value")


def load_ui_design(arc_dir, tree, images):
    """Validate the saved design without rerunning synthesis or imposing a new fixture budget."""
    from infrastructure.stages.frontend.ui.design import (
        validate_design as validate_ui_design,
    )

    design = read_artifact(arc_dir, "ui_design.json")
    if not isinstance(design, dict) or not isinstance(design.get("pages"), dict):
        raise ValueError("Saved UI design must contain a pages object")
    validate_ui_design(design, tree, images, max_fixtures=None, complete=True)
    return design


def load_ui_context(arc_dir, input_dir):
    """Load only requirement and image evidence; presentation does not depend on backend artifacts."""
    raw = read_artifact(arc_dir, "requirements.json")
    tree = RequirementTree(raw)
    analysis = read_artifact(arc_dir, "visual_analysis.json")
    images, nodes = {}, {}

    def visit(node):
        """Index raw requirements and their concrete image definitions, rejecting missing files or conflicting evidence."""
        nodes[node["id"]] = node
        description = node.get("description", {})
        for image in (
            description.get("image", []) if isinstance(description, dict) else []
        ):
            if (
                not isinstance(image, dict)
                or not isinstance(image.get("id"), str)
                or not isinstance(image.get("reference"), str)
            ):
                raise ValueError(
                    "Each frontend image definition needs id and reference"
                )
            if REFERENCE.fullmatch(image["reference"]):
                continue
            source = (input_dir / image["reference"]).resolve()
            if not source.is_relative_to(input_dir.resolve()) or not source.is_file():
                raise ValueError(
                    f"Missing input image or image escapes input: {image['reference']}"
                )
            record = {**image, "analysis": analysis.get(image["reference"], {})}
            images[image["id"]] = record
        for child in node.get("children", []):
            visit(child)

    visit(raw)
    contexts = {}
    supplied_tests = reference_tests(input_dir)
    for rid in tree.requirements:
        node = nodes[rid]
        direct = {key: value for key, value in node.items() if key != "children"}
        refs = set(REFERENCE.findall(json.dumps(direct)))
        description = node.get("description", {})
        for image in (
            description.get("image", []) if isinstance(description, dict) else []
        ):
            if image.get("id") in images:
                refs.add(image["id"])
        contexts[rid] = {
            **tree.requirements[rid],
            "steps": [tree.steps[sid] for sid in tree.own_steps[rid]],
            "images": {key: images[key] for key in sorted(refs) if key in images},
        }
        if supplied_tests:
            contexts[rid]["reference_tests"] = supplied_tests
    return tree, images, contexts


def load_frontend_context(arc_dir, input_dir):
    """Combine visual requirements with validated database and API artifacts for design stages."""
    tree, schema, obligations = load_context(arc_dir)
    _, images, contexts = load_ui_context(arc_dir, input_dir)
    backend = read_artifact(arc_dir, "backend_apis.json")
    contracts = read_artifact(arc_dir, "backend_contracts.json")
    validate_design(backend, obligations, field_symbols(schema), tree=tree)
    validate_contracts(contracts, backend)
    return tree, schema, obligations, contracts, images, contexts


def behavior_contexts(contexts):
    """Behavior stages use structured requirement text without repeated visual evidence."""
    return {
        rid: {key: value for key, value in context.items() if key != "images"}
        for rid, context in contexts.items()
    }
