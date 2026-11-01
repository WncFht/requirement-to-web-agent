"""Reject provably contradictory generated assertions before test freezing."""

import os
import re


def validate_backend_test(source):
    """Detect only the narrow total-string helper observed in a real failed run.

    JSON.stringify(x ?? {}) always returns a nonempty string. Negating that
    result cannot test header absence. Unsupported source shapes are left to
    existing compilation and RED/GREEN gates; this is not a JS theorem prover.
    """
    if os.getenv("ARC_LEGACY_TEST_SANITY", "0") == "1":
        return
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
