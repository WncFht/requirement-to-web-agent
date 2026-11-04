"""Narrow, source-backed control contracts; never read frozen acceptance suites."""

import re


KINDS = {"page", "container", "form", "input", "checkbox", "select", "button", "text",
    "heading", "link", "list", "item", "image", "alert", "table"}


def control_contract(requirement):
    """Extract explicit English lists/quoted labels; unrecognized prose stays prose.

    This is deliberately not a general natural-language specification parser.
    Every extracted control retains its exact source sentence for audit.
    """
    description = requirement.get("description", "")
    text = description.get("text", "") if isinstance(description, dict) else description
    controls = []
    radio_groups = []
    route = re.search(r"\bpage\s+(/[^\s,;]*)", text)
    fields = re.search(r"\bcontains\s+(.+?)\s+fields\.", text)
    if fields:
        for label in re.split(r",\s*(?:and\s+)?|\s+and\s+", fields.group(1)):
            label = label.strip()
            if label:
                controls.append({"kind": "field", "name": label, "evidence": fields.group(0)})
    for control in list(controls):
        label = re.escape(control["name"])
        options = re.search(label + r"\s+(includes|offers)\s+([^;.]+)", text)
        if options:
            values = [x.strip() for x in re.split(r",\s*(?:and\s+)?|\s+and\s+", options.group(2))]
            if options.group(1) == "offers":
                radio_groups.append({"name": control["name"], "options": values, "evidence": options.group(0)})
                controls.remove(control)
                controls.extend({"kind": "radio", "name": value, "value": value,
                    "group": control["name"], "evidence": options.group(0)} for value in values)
            else:
                control.update(kind="select", options=values)
        if "password" in control["name"].lower() and re.search(r"[Pp]assword.*conceal", text):
            control.update(kind="input", input_type="password")
    patterns = (
        ("checkbox", r'checkbox is labeled "([^"]+)"'),
        ("button", r'button is labeled "([^"]+)"'),
        ("input", r'field has the placeholder and accessible name "([^"]+)"'),
        ("input", r'password field is labeled "([^"]+)"'),
    )
    for kind, pattern in patterns:
        for match in re.finditer(pattern, text):
            item = {"kind": kind, "name": match.group(1), "evidence": match.group(0)}
            if "placeholder and accessible name" in match.group(0):
                item["placeholder"] = item["name"]
            if "password field" in match.group(0):
                item["input_type"] = "password"
            controls.append(item)
    return {"requirement": requirement.get("id"), "route": route.group(1) if route else None,
        "controls": controls, "radio_groups": radio_groups, "coverage": "explicit field lists and quoted labels only"}


def normalize_controls(design):
    """Only radio is a supported alias; unknown kinds cannot disappear from tests."""
    for uid, element in design["elements"].items():
        kind = element.get("type", "page" if element.get("parent") is None else "container")
        if kind == "radio":
            element["type"] = "input"
            element.setdefault("prop", {})["input_type"] = "radio"
            kind = "input"
        if kind not in KINDS:
            raise ValueError(f"{uid}: unsupported UI type {kind!r}; use a supported element kind")


def validate_control_contract(design, contract):
    """Require source names/types in the contract's page, independently of model IDs."""
    if not contract.get("controls"):
        return
    from infrastructure.stages.frontend.ui.design import page_elements
    pages = [pid for pid, page in design["pages"].items() if page["route"] == contract["route"]]
    if len(pages) != 1:
        raise ValueError(f"{contract['requirement']}: expected one page at {contract['route']}")
    elements = page_elements(design, pages[0])
    failures = []
    for required in contract["controls"]:
        matches = []
        for uid, element in elements.items():
            kind, prop = element.get("type"), element.get("prop", {})
            if prop.get("label", prop.get("text")) != required["name"]:
                continue
            expected = required["kind"]
            valid = (kind in {"input", "select"} if expected == "field" else
                kind == "input" and prop.get("input_type") == "radio" if expected == "radio" else kind == expected)
            valid = valid and all(prop.get(key) == required[key] for key in ("input_type", "placeholder", "href", "value") if key in required)
            if "options" in required:
                valid = valid and set(required["options"]).issubset(prop.get("options", []))
            if valid:
                matches.append(uid)
        if len(matches) != 1:
            failures.append(f"require exactly one {required['kind']} named {required['name']!r}; found {len(matches)}. Source: {required['evidence']}")
    if failures:
        raise ValueError(f"{contract['requirement']}: " + "\n".join(failures) +
            "\nPreserve each source name in prop.label (button/link text in prop.text); put visual required markers outside the accessible name.")


def radio_group_assertions(contract):
    """Browser assertions for original named single-choice fields and membership."""
    import json
    lines = []
    for group in contract.get("radio_groups", []):
        target = f'page.getByRole("radiogroup", {{ name: {json.dumps(group["name"])}, exact: true }})'
        lines.extend([f'  await expect({target}).toHaveCount(1);', f'  await expect({target}).toBeVisible();'])
        for option in group["options"]:
            radio = target + f'.getByRole("radio", {{ name: {json.dumps(option)}, exact: true }})'
            lines.extend([f'  await expect({radio}).toHaveCount(1);', f'  await expect({radio}).toBeVisible();'])
    return lines


def radio_group_suite(contracts):
    """Additive requirement regression; never rewrite an already frozen suite."""
    import json
    lines = ['import { test, expect } from "@playwright/test";', '']
    for contract in contracts:
        assertions = radio_group_assertions(contract)
        if not assertions:
            continue
        lines.extend([f'test({json.dumps(contract["requirement"] + " / named radio group")}, async ({{ page }}) => {{',
            f'  await page.goto({json.dumps(contract["route"])});', *assertions, '});', ''])
    return "\n".join(lines)
