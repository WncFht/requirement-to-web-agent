"""Offline context candidate; does not change production repair permissions or gates."""

from copy import deepcopy
import posixpath
import re


def select_related(payload, owned_paths):
    """Retain task-owned sources, test/interfaces and local import closure.

    The caller must establish semantic ownership. Kept permissions are unchanged;
    omitted paths are an audit inventory, not a new read tool or repair capability.
    This candidate is not enabled in the compiler until stage replay validates it.
    """
    result = deepcopy(payload)
    files = result.get("files", {})
    selected = {name for name in files if not name.startswith(("frontend/src/", "backend/src/"))}
    selected.update(name for name in owned_paths if name in files)
    selected.update(name for name in files if name.endswith(("/ui-runtime.ts", "/api/types.ts", "/style.css")))
    pending = list(selected)
    seen = set()
    while pending:
        name = pending.pop()
        if name in seen or name not in files:
            continue
        seen.add(name)
        source = files[name].get("content") or ""
        for imported in re.findall(r'''(?:\bfrom\s*|\bimport\s*(?:\(\s*)?|\brequire\(\s*)["'](\.[^"']+)["']''', source):
            base = posixpath.normpath(posixpath.join(posixpath.dirname(name), imported))
            stem = base[:-3] if base.endswith(".js") else base[:-4] if base.endswith(".jsx") else base
            candidates = [base, *(stem + ext for ext in (".ts", ".tsx", ".js", ".jsx", ".json", ".css")),
                *(base + "/index" + ext for ext in (".ts", ".tsx", ".js", ".jsx"))]
            target = next((path for path in candidates if path in files), None)
            if target and target not in selected:
                selected.add(target)
                pending.append(target)
    omitted = sorted(set(files) - selected)
    result["files"] = {name: item for name, item in files.items() if name in selected}
    return result, {"omitted": omitted, "kept": sorted(result["files"]),
        "status": "OFFLINE_CANDIDATE_NOT_ENABLED", "ownership_paths": sorted(owned_paths)}
