"""Bound single-handler creation inputs while retaining complete final repair context."""

from copy import deepcopy
from infrastructure.shared.models.context_order import stable_creation_first

from infrastructure.stages.frontend.interactions.design import api_ids


def creation_context(context, event_id, event_paths, page_paths):
    """Select one event and all of its triggers, preserving every available data binding.

    Event descriptions are prose and have no reliable read-set. Keep all page
    bindings rather than guessing dependencies from write permissions or tokens.
    Full pages, other handlers and external tests remain in final repair calls.
    """
    event = context["events"][event_id]
    triggers = {
        key: trigger
        for key, trigger in context["triggers"].items()
        if trigger["action"] == event_id
    }
    sources = {trigger["source"] for trigger in triggers.values()}
    bindings = {}
    elements = {}
    pages = {}
    for pid, page in context["page_subtrees"].items():
        pages[pid] = {key: page[key] for key in ("name", "route", "root")}
        for key, value in page["bindings"].items():
            if key in bindings and bindings[key] != value:
                raise ValueError(f"Conflicting creation binding: {key}")
            bindings[key] = value
        elements.update(
            {key: value for key, value in page["elements"].items() if key in sources}
        )
    requirement = {
        key: value
        for key, value in context["requirement"].items()
        if key != "reference_tests"
    }
    return stable_creation_first(
        deepcopy(
            {
                "creation_scope": "Implement only this handler from its complete contract and triggers. Final repair receives full pages, handlers and frozen tests.",
                "requirement": requirement,
                "page_inventory": pages,
                "source_elements": elements,
                "frontend_data": bindings,
                "triggers": triggers,
                "events": {event_id: event},
                "contracts": {event_id: context["contracts"][event_id]},
                "backend_apis": {
                    key: context["backend_apis"][key] for key in sorted(api_ids(event))
                },
                "implementation_paths": {event_id: event_paths[event_id]},
                "page_paths": page_paths,
                "target_event_ids": [event_id],
            }
        )
    )
