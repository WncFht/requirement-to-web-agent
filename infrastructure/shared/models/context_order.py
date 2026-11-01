"""Opt-in stable-prefix ordering, preserving every field, byte value and edit permission."""

import os


def cache_prefix_enabled():
    return os.getenv("ARC_CACHE_PREFIX", "1") == "1"


def stable_first(value, keys):
    if not cache_prefix_enabled():
        return value
    if os.getenv("ARC_CACHE_PREFIX_V2", "0") == "1" and "event_id" in value:
        keys = (*keys, "all_requirement_uses", "backend_apis")
    first = {key: value[key] for key in keys if key in value}
    return {**first, **value}


def stable_creation_first(value):
    if not cache_prefix_enabled() or os.getenv("ARC_CACHE_PREFIX_V2", "0") != "1":
        return value
    return stable_first(
        value,
        (
            "creation_scope",
            "page_inventory",
            "frontend_data",
            "page_paths",
            "requirement",
        ),
    )


def file_order(files, writable):
    if not cache_prefix_enabled():
        return sorted(files)
    # ui-events changes as handlers are registered. The runtime/API wiring is
    # shared across event creation calls, so put it before pages and registries.
    priority = {
        "frontend/src/ui-runtime.ts": 0,
        "frontend/src/ui-api.ts": 1,
        "frontend/src/ui-events.ts": 4,
    }
    return sorted(
        files, key=lambda path: (priority.get(path, 3 if path in writable else 2), path)
    )
