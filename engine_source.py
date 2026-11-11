"""Select the repository-owned engine before any minisweagent import."""

import json
import sys
from pathlib import Path

ENGINE_ROOT = Path(__file__).resolve().parent / "vendor" / "mini-swe-agent"
ENGINE_SRC = ENGINE_ROOT / "src"


def select_engine_source():
    if not (ENGINE_SRC / "minisweagent" / "__init__.py").is_file():
        raise RuntimeError(f"Bundled mini-swe-agent source missing: {ENGINE_SRC}")
    loaded = sys.modules.get("minisweagent")
    if loaded is not None and not Path(loaded.__file__).resolve().is_relative_to(ENGINE_SRC):
        raise RuntimeError("A different minisweagent was already imported; start a fresh process")
    source = str(ENGINE_SRC)
    if source in sys.path:
        sys.path.remove(source)
    sys.path.insert(0, source)


def engine_identity():
    select_engine_source()
    import minisweagent

    upstream = json.loads((ENGINE_ROOT / "UPSTREAM.json").read_text())
    return {"engine_source": str(Path(minisweagent.__file__).resolve()),
            "engine_version": minisweagent.__version__,
            "engine_upstream_commit": upstream["commit"]}
