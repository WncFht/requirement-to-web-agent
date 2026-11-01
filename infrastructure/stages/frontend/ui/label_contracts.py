"""Keep exact label locators aligned with external browser interaction contracts."""

import os


def label_instructions():
    """Keep the historical prompt available alongside the additional label gate."""
    if os.getenv("ARC_LEGACY_LABEL_LOCATORS", "0") == "1":
        return ""
    return """Exact label lookup is an external interaction contract, separate from accessible name.
Every labeled editable control must resolve uniquely through getByLabel(label,{exact:true})
to that actual control. Give the control an explicit aria-label equal to prop.label when
decorative required asterisks or other extra label text are present. aria-hidden on a
label's star alone does NOT guarantee exact getByLabel matching, including passwords.
Preserve password input types and native label associations. Do not remove validation
or alter frozen tests to fix a label. Preserve these names during later source repairs.
"""
