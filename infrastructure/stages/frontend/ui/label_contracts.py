"""Keep exact label locators aligned with external browser interaction contracts."""

import os


def radio_group_instructions():
    if os.getenv("ARC_LEGACY_RADIO_CONTAINMENT", "0") == "1":
        return ""
    return """A prop.role=radiogroup element is the common semantic wrapper CONTAINING its radio inputs.
Put that group's data-testid, role=radiogroup and exact aria-label on this wrapper,
not on a left-hand label column with the inputs in a sibling column outside it.
getByTestId(group).getByRole('radio',{name: optionLabel,exact:true}) must resolve
to the actual corresponding radio input. Preserve native radio names/values,
labels, checked state, IR hierarchy and frozen tests during all later repairs.
"""


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
