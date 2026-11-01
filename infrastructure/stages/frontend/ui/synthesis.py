"""Step 09 orchestration: retrieve pages, propose UI/data, validate, and publish.

All leaf requirements are designed before step 10 implements any UI. Reuse is
page-first: retrieval returns the corresponding UI/data subtree, not disconnected
components. Prompts and structural validation live in ui/design.py."""

import json
import os
from copy import deepcopy

from infrastructure.stages.frontend.ui.design import (
    INSTRUCTIONS,
    apply_proposal,
    empty_design,
    page_elements,
    validate_design,
)
from infrastructure.stages.frontend.ui.proposals import (
    INSTRUCTIONS as EXAMPLE_INSTRUCTIONS,
)
from infrastructure.shared.rag.pages import PageRetriever
from infrastructure.stages.frontend.context import validate_reference_controls
from infrastructure.utils.files import save_json

VISIBILITY_RULES = """Check every fixture's derived visibility against the requirement BEFORE returning.
Supplied reference_tests are read-only external interaction contracts. Honor their
exact accessible labels, roles and routes when choosing controls. Date entry queried
as a textbox needs a textbox-compatible control; do not infer a different role from
the screenshot. A radiogroup is a labeled container (prop.role=radiogroup), with
input children input_type=radio, prop.value for each option and one shared selection
binding; a select is not interchangeable with that externally required role.
Treat filenames as historical labels, matching tests to behavior.
A visibility predicate represents the whole business condition, not just readiness.
If display requires two conditions, use a dedicated boolean binding representing the
combined condition and document how events maintain it; a single {var,equals} rule
cannot silently stand in for a conjunction. For authentication: signed-out entry
links must be hidden in signed-in fixtures and shown in signed-out fixtures; the
username has the opposite visibility. Readiness alone is not signed-out identity.
Include explicit values for these boolean bindings in all affected fixtures.
Do not contradict requirement text with props merely to reproduce a static image.
"""


def bind_requirement_image_pages(design, requirement, rid):
    """Bind image-backed pages to the current requirement when the page hint is unambiguous."""
    owned = list(design["requirements"].get(rid, []))
    images = requirement.get("images", {})
    image_records = images.values() if isinstance(images, dict) else images
    for image in image_records:
        if not isinstance(image, dict):
            continue
        image_id, page_hint = image.get("id"), image.get("page")
        # The requirement's explicit page hint is authoritative. The model may
        # omit the redundant page.images entry when creating a new page.
        if page_hint in design["pages"]:
            page = design["pages"][page_hint]
            page.setdefault("images", [])
            if image_id not in page["images"]:
                page["images"].append(image_id)
            candidates = [page_hint]
        else:
            candidates = [
                pid
                for pid, page in design["pages"].items()
                if image_id in page.get("images", [])
            ]
        if len(candidates) != 1:
            continue
        root = design["pages"][candidates[0]]["root"]
        if root in design["elements"]:
            if root not in owned:
                owned.append(root)
    design["requirements"][rid] = owned


def synthesize_ui(
    arc_dir,
    tree,
    schema,
    contracts,
    images,
    contexts,
    model,
    console,
    top_k=3,
    max_fixtures=3,
):
    """Design UI/data for all leaf requirements using page-first retrieval.

    Show existing/retrieved pages, ask for an incremental proposal, and feed
    validation errors back for bounded retries. Accepted designs are checkpointed
    per requirement (ui_design.json + ui_design_progress.json), so a failed
    requirement only redoes itself on rerun unless ARC_UI_DESIGN_FRESH=1.
    Implementation and browser tests belong to step 10."""
    design, retriever = empty_design(), PageRetriever()
    completed = []
    fresh = os.getenv("ARC_UI_DESIGN_FRESH", "0") == "1"
    progress_path, design_path = (
        arc_dir / "ui_design_progress.json",
        arc_dir / "ui_design.json",
    )
    if not fresh and design_path.is_file():
        try:
            saved = json.loads(design_path.read_text(encoding="utf-8-sig"))
            design = {
                key: deepcopy(saved.get(key, {}))
                for key in ("pages", "elements", "bindings", "requirements", "steps")
            }
            if progress_path.is_file():
                completed = list(
                    json.loads(progress_path.read_text(encoding="utf-8-sig")).get(
                        "completed", []
                    )
                )
            else:
                completed = [
                    rid for rid, owned in design["requirements"].items() if owned
                ]
            console.show(
                "UI/data design resume",
                f"Loaded checkpoint with {len(completed)} completed leaf requirements: {sorted(completed)}",
            )
        except (OSError, ValueError, json.JSONDecodeError) as error:
            console.show(
                "UI/data design resume unavailable", f"Starting fresh ({error})"
            )
            design, completed = empty_design(), []
    failures = []
    for rid in tree.requirements:
        if tree.children[rid]:
            design["requirements"][rid] = []
            for sid in tree.own_steps[rid]:
                design["steps"][sid] = []
            console.show(
                f"{rid} | Skip non-leaf UI/data analysis",
                "Only leaf requirements are analyzed. Organizational parents do not generate or inherit UI nodes.",
            )
    for number, rid in enumerate(tree.leaves, 1):
        if rid in completed:
            console.show(
                f"UI/data design {number}/{len(tree.leaves)} {rid} | Checkpoint hit",
                "Already designed in an earlier run; skipping. Set ARC_UI_DESIGN_FRESH=1 to redesign.",
            )
            continue
        requirement = contexts[rid]
        label = f"UI/data design {number}/{len(tree.leaves)} {rid}"
        console.show(
            label + " | 1. Requirement and steps",
            json.dumps(requirement, ensure_ascii=False, indent=2),
        )
        console.show(
            label + " | 2. All Existing Pages",
            json.dumps(design["pages"], ensure_ascii=False, indent=2),
        )
        retrieved = retriever.retrieve(requirement, design, top_k)
        console.show(
            label + " | 3. Retrieved page subtrees (RAG)",
            json.dumps(retrieved, ensure_ascii=False, indent=2),
        )
        request = {
            "requirement": requirement,
            "retrieved_pages": retrieved["pages"],
            "all_pages": {
                pid: {key: page[key] for key in ("name", "route", "root", "images")}
                for pid, page in design["pages"].items()
            },
            "schema": schema["entities"],
            "direct_apis": {
                aid: contracts["apis"][aid] for aid in contracts["requirements"][rid]
            },
            "max_fixtures": max_fixtures,
        }
        for attempt in range(1, 4):
            response, updated = None, None
            try:
                response = model.generate_json(
                    INSTRUCTIONS
                    + "\n\n"
                    + EXAMPLE_INSTRUCTIONS
                    + (
                        ""
                        if os.getenv("ARC_LEGACY_UI_PREDICATES", "0") == "1"
                        else "\n\n" + VISIBILITY_RULES
                    ),
                    request,
                )
                proposal = response
                updated = apply_proposal(
                    design,
                    proposal,
                    rid,
                    tree,
                    images,
                    retrieved["pages"],
                    max_fixtures,
                )
                bind_requirement_image_pages(updated, requirement, rid)
                validate_reference_controls(updated, requirement)
                break
            except ValueError as error:
                correction = {"error": str(error), "previous_response": response}
                message = str(error)
                if isinstance(error, json.JSONDecodeError):
                    correction["invalid_response"] = error.doc
                    correction["instruction"] = (
                        "Follow the complete JSON examples exactly: one outer object containing pages, elements, bindings, requirement_ui, step_ui. Use ordinary objects, not patch/entries arrays. Return complete records for changed IDs; omit unchanged IDs."
                    )
                    message += "\nInvalid JSON response (excerpt):\n" + error.doc[:3000]
                elif response is not None:
                    message += (
                        "\nRejected proposal (excerpt):\n"
                        + json.dumps(response, ensure_ascii=False, indent=2)[:3000]
                    )
                console.show(label + f" | Validation failed ({attempt}/3)", message)
                if attempt == 3:
                    failures.append(f"{rid}: {error}")
                    console.show(
                        label + " | Deferred failure",
                        f"{rid} is recorded; other requirements continue. Rerun step 09 to retry it.",
                    )
                    break
                request["correction"] = correction
        if updated is None:
            save_json(progress_path, {"completed": sorted(set(completed))})
            continue
        console.show(
            label + " | 4. Validated incremental UI/data changes",
            json.dumps(proposal, ensure_ascii=False, indent=2),
        )
        design = updated
        completed.append(rid)
        save_json(design_path, design)
        save_json(progress_path, {"completed": sorted(set(completed))})
    if failures:
        raise ValueError(
            "UI/data design failed for some requirements after 3 proposals each: "
            + "; ".join(failures)
        )
    validate_design(design, tree, images, max_fixtures, complete=True)
    save_json(arc_dir / "ui_design.json", design)
    console.show(
        "UI/data design complete for ALL requirements",
        f"Saved {arc_dir / 'ui_design.json'}\nRun 10_implement_ui.py for existence tests and UI implementation. Interactions belong to step 11.",
    )
    return design
