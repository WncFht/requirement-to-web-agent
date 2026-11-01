"""Reject provably contradictory generated assertions before test freezing."""

import ast
import json
import os
import re


def validate_backend_test(source):
    """Detect narrow total-string contradictions observed in real failed runs.

    JSON.stringify(x ?? {}) always returns a nonempty string. Negating that
    result cannot test header absence. Unsupported source shapes are left to
    existing compilation and RED/GREEN gates; this is not a JS theorem prover.
    """
    if os.getenv("ARC_LEGACY_TEST_SANITY", "0") == "1":
        return
    literal = r"""(?:"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')"""
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
                raise ValueError(
                    "Contradictory generated test: JSON.stringify cannot equal a "
                    "non-JSON string literal. For secret absence, assert "
                    "JSON.stringify(body).includes(secret) is false, preserving "
                    "all response and no-write assertions before freezing."
                ) from error
    pattern = re.compile(
        r"function\s+(\w+)\s*\([^)]*\)\s*(?::[^{}]+)?\{\s*"
        r"return\s+JSON\.stringify\(\s*\w+\s*\?\?\s*\{\s*\}\s*\)\s*;?\s*\}"
    )
    for match in pattern.finditer(source):
        helper = re.escape(match.group(1))
        if re.search(r"\bassert\.ok\(\s*!\s*" + helper + r"\s*\(", source):
            raise ValueError(
                "Contradictory generated test: "
                + match.group(1)
                + " returns JSON.stringify(value ?? {}), always a nonempty string. "
                "Its negation cannot pass for any headers. Assert the actual "
                "set-cookie property is absent for rejection, preserving the "
                "contract's no-session/no-write expectations. Repair this test "
                "before it is frozen; application changes cannot satisfy it."
            )
