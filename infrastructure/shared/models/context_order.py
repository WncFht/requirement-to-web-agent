"""Opt-in stable-prefix ordering, preserving every field, byte value and edit permission."""

import os


def cache_prefix_enabled():
    return os.getenv("ARC_CACHE_PREFIX", "0") == "1"


def stable_first(value, keys):
    if not cache_prefix_enabled():
        return value
    first = {key: value[key] for key in keys if key in value}
    return {**first, **value}


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
