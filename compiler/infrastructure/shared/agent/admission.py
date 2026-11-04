"""Reject specific contradictions observed in runs before tests are frozen."""

import ast
import json
import re


def validate_ui_controls(design):
    """Require resolvable display values and explicit native radio option values."""
    from infrastructure.stages.frontend.ui.contracts import normalize_controls
    normalize_controls(design)
    roots = {page["root"] for page in design["pages"].values()}
    for uid, element in design["elements"].items():
        current, seen = uid, set()
        while current is not None:
            if current in seen or current not in design["elements"]:
                raise ValueError(f"{uid}: cyclic or missing UI parent {current!r}")
            seen.add(current)
            parent = design["elements"][current].get("parent")
            if parent is None and current not in roots:
                raise ValueError(f"{uid}: UI subtree has no page root")
            current = parent
    bindings = design["bindings"]
    for uid, element in design["elements"].items():
        variables = list(element.get("data", []))
        prop = element.get("prop", {})
        if isinstance(prop.get("visible"), dict):
            variables.append(prop["visible"]["var"])
        for variable in variables:
            if variable not in bindings or "initial" not in bindings[variable]:
                raise ValueError(f"{uid} references missing initial binding {variable}; define it before generating tests")
        if element.get("type") == "input" and prop.get("input_type") == "radio":
            if not isinstance(prop.get("value"), str):
                raise ValueError(f"{uid}: radio prop.value must explicitly name its string option value")
            if not element.get("data") or not isinstance(bindings[element["data"][0]]["initial"], str):
                raise ValueError(f"{uid}: radio must bind a string selection; checked state is selection == prop.value")
    for pid, page in design["pages"].items():
        for name, fixture in page.get("fixtures", {}).items():
            missing = set(fixture) - set(bindings)
            if missing:
                raise ValueError(f"{pid}/{name}: fixture references undefined bindings {sorted(missing)}")


def validate_backend_test(source):
    """Reject two known unsatisfiable JSON-string assertions, not arbitrary JS."""
    literal = r'''(?:"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')'''
    stringify = r"JSON\.stringify\(\s*[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*\s*\)"
    for pattern in (
        rf"\bassert\.(?:equal|strictEqual)\(\s*({literal})\s*,\s*{stringify}\s*[,)]",
        rf"\bassert\.(?:equal|strictEqual)\(\s*{stringify}\s*,\s*({literal})\s*[,)]",
    ):
        for match in re.finditer(pattern, source):
            try:
                value = ast.literal_eval(match.group(1))
            except (ValueError, SyntaxError):
                continue
            try:
                json.loads(value)
            except ValueError as error:
                raise ValueError("Contradictory test: JSON.stringify cannot equal a non-JSON string; check the intended response field") from error
    helper = re.compile(r"function\s+(\w+)\s*\([^)]*\)\s*(?::[^{}]+)?\{\s*"
        r"return\s+JSON\.stringify\(\s*\w+\s*\?\?\s*\{\s*\}\s*\)\s*;?\s*\}")
    for match in helper.finditer(source):
        if re.search(r"\bassert\.ok\(\s*!\s*" + re.escape(match.group(1)) + r"\s*\(", source):
            raise ValueError("Contradictory test: JSON.stringify(value ?? {}) is nonempty; assert the required header absence directly")


def validate_e2e_test(source):
    """Presentation fixtures cannot establish business state in browser E2E."""
    if re.search(r'''__ARC_UI_FIXTURE__(?:["']\])?\s*=''', source):
        raise ValueError("E2E cannot assign __ARC_UI_FIXTURE__; establish Given state and drive real browser actions before freezing")
