"""Validate explicitly composed generated pages; never label it a fresh full generation."""

import argparse
from copy import deepcopy
from hashlib import sha256
from importlib import import_module
import json
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "compiler"), str(ROOT / "scripts")]
from stage_replay import fresh, fingerprint
from infrastructure.shared.project.initialize import initialize_project
from infrastructure.shared.agent.checkpoints import capture
from infrastructure.shared.agent.frozen_tests import freeze_tests, verify_frozen_tests
from infrastructure.shared.agent.recovery import final_checks
from infrastructure.stages.backend.testing import (
    BackendChecks,
    require_green as backend_green,
)
from infrastructure.stages.frontend.context import load_ui_design, load_ui_context
from infrastructure.stages.frontend.ui.design import page_elements
from infrastructure.utils.files import save_json
from infrastructure.utils.presentation.console import DemoConsole
from infrastructure.utils.presentation.logging import console_log


def merge_page(base, replacement, page_id):
    """Replace one complete generated subtree, preserving other pages and ownership."""
    design = deepcopy(base)
    removed = set(page_elements(design, page_id))
    incoming = page_elements(replacement, page_id)
    if set(incoming) & (set(design["elements"]) - removed):
        raise ValueError("Replacement page collides with another page's element IDs")
    design["elements"] = {
        key: value for key, value in design["elements"].items() if key not in removed
    }
    design["elements"].update(incoming)
    design["pages"][page_id] = deepcopy(replacement["pages"][page_id])
    used = {name for node in incoming.values() for name in node.get("data", [])}
    used.update(
        node["prop"]["visible"]["var"]
        for node in incoming.values()
        if isinstance(node.get("prop", {}).get("visible"), dict)
    )
    for name in used:
        if name not in replacement["bindings"]:
            raise ValueError("Replacement binding missing: " + name)
        outside = any(
            name in node.get("data", [])
            or (
                isinstance(node.get("prop", {}).get("visible"), dict)
                and node["prop"]["visible"]["var"] == name
            )
            for uid, node in base["elements"].items()
            if uid not in removed
        )
        if outside:
            # Preserve canonical declarations used by the inherited pages. Prose
            # constraint/source descriptions do not change the runtime projection.
            previous = base["bindings"].get(name, {})
            if any(
                previous.get(key) != replacement["bindings"][name].get(key)
                for key in ("dtype", "initial")
            ):
                raise ValueError("Shared runtime binding definitions differ: " + name)
        else:
            design["bindings"][name] = deepcopy(replacement["bindings"][name])
    for kind in ("requirements", "steps"):
        keys = set(design[kind]) | set(replacement[kind])
        design[kind] = {
            key: [uid for uid in design[kind].get(key, []) if uid not in removed]
            + [uid for uid in replacement[kind].get(key, []) if uid in incoming]
            for key in keys
        }
    referenced = {
        name for node in design["elements"].values() for name in node.get("data", [])
    }
    referenced.update(
        node["prop"]["visible"]["var"]
        for node in design["elements"].values()
        if isinstance(node.get("prop", {}).get("visible"), dict)
    )
    for page in design["pages"].values():
        referenced.update(
            name for fixture in page.get("fixtures", {}).values() for name in fixture
        )
    design["bindings"] = {
        name: record
        for name, record in design["bindings"].items()
        if name in referenced
    }
    design.pop("control_contracts", None)
    return design


def prepare(base, page_trial, output, page_id):
    base, page_trial = Path(base).resolve(), Path(page_trial).resolve()
    page_identity = json.loads((page_trial / "identity.json").read_text())
    if json.loads((page_trial / "result.json").read_text())["status"] != "GREEN":
        raise ValueError("Replacement page must have passed its native gates")
    replacement = json.loads(
        (Path(page_identity["design_trial"]) / "ui_design.json").read_text()
    )
    base_design = json.loads((base / ".arc/ui_design.json").read_text())
    design = merge_page(base_design, replacement, page_id)
    output = fresh(output)
    initialize_project(output)
    shutil.copytree(
        base / "backend",
        output / "backend",
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(
            "node_modules", "dist", "*.db", "*.db-wal", "*.db-shm"
        ),
    )
    shutil.copytree(base / "node_modules", output / "node_modules", symlinks=True)
    source_files = {}
    for name in (
        "requirements.json",
        "visual_analysis.json",
        "db_schema.json",
        "db_obligations.json",
        "backend_apis.json",
    ):
        source = base / ".arc" / name
        target = output / ".arc" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
        source_files[str(source)] = sha256(source.read_bytes()).hexdigest()
    old_index = json.loads((base / ".arc/implementation_paths.json").read_text())
    replacement_index = json.loads(
        (page_trial / ".arc/implementation_paths.json").read_text()
    )
    index = {key: deepcopy(old_index[key]) for key in ("api", "backend_test")}
    index["page"] = {}
    for pid in design["pages"]:
        donor = page_trial if pid == page_id else base
        relative = (
            replacement_index["page"][pid] if pid == page_id else old_index["page"][pid]
        )
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((donor / relative).read_bytes())
        index["page"][pid] = relative
        source_files[str(donor / relative)] = sha256(target.read_bytes()).hexdigest()
    for source in (base / "backend").rglob("*"):
        if (
            source.is_file()
            and source.suffix in {".ts", ".sql", ".json", ".mjs"}
            and "dist" not in source.parts
        ):
            source_files[str(source)] = sha256(source.read_bytes()).hexdigest()
    save_json(output / ".arc/implementation_paths.json", index)
    save_json(output / ".arc/ui_design.json", design)
    tree, _, _ = load_ui_context(output / ".arc", ROOT / "input")
    design = load_ui_design(output / ".arc", tree)
    save_json(output / ".arc/ui_design.json", design)
    freeze_tests(output, list(index["backend_test"].values()))
    provenance = {
        "kind": "explicit composition of generated artifacts",
        "complete_generation": False,
        "backend_source": str(base),
        "replacement_page": str(page_trial),
        "page_id": page_id,
        "source_files": source_files,
        "compiler_files": fingerprint(),
        "limitations": "Backend and other pages are inherited final artifacts, not a historical pre-stage snapshot. All gates must run again.",
    }
    save_json(output / "composition.json", provenance)
    return output


def run(base, trial, output, page_id, ledger, checkpoints):
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    os.environ.setdefault("MODEL", "deepseek-flash")
    os.environ["ARC_EXPERIMENT_BUDGET"] = str(Path(ledger).resolve())
    os.environ["MAX_OUTPUT_TOKENS"] = str(
        json.loads(Path(ledger).read_text())["max_output_tokens"]
    )
    output = prepare(base, trial, output, page_id)
    report = {
        "kind": "composition validation",
        "complete_generation": False,
        "status": "RUNNING",
        "stages": {},
    }
    try:
        with console_log(
            output, stage="Composition backend revalidation", model_log=True
        ):
            checks = BackendChecks(output)
            apis = json.loads((output / ".arc/backend_apis.json").read_text())["apis"]
            checks.http_apis = apis
            files = list(
                json.loads((output / ".arc/implementation_paths.json").read_text())[
                    "backend_test"
                ].values()
            )
            verification = final_checks(
                DemoConsole(False),
                typecheck=(checks.typecheck, None),
                tests=(lambda: checks.tests(files), backend_green),
                build=(checks.build, None),
            )
            backend_report = {
                "status": "GREEN"
                if all(v["status"] == "GREEN" for v in verification.values())
                else "FAILED",
                "kind": "inherited generated backend, fresh direct+HTTP checks",
                "verification": verification,
            }
            save_json(output / ".arc/backend_tdd.json", backend_report)
            if backend_report["status"] != "GREEN":
                raise ValueError("Inherited backend failed fresh validation")
            report["stages"]["backend_revalidation"] = "GREEN"
        stages = [
            ("10_implement_ui", "implement_frontend_ui", {"max_turns": 1}),
            (
                "11_design_frontend_triggers",
                "design_frontend_triggers",
                {"max_attempts": 2},
            ),
            (
                "12_implement_frontend_tdd",
                "implement_frontend_triggers",
                {"max_turns": 2},
            ),
        ]
        for module, function, options in stages:
            capture(output, Path(checkpoints).resolve() / module, stage=module)
            with console_log(output, stage=module, model_log=True):
                result = getattr(import_module(module), function)(
                    ROOT / "input", output / ".arc", **options
                )
            verify_frozen_tests(output)
            status = result.get("status", "GREEN")
            report["stages"][module] = status
            save_json(output / "composition-result.json", report)
            if status != "GREEN":
                raise ValueError("Composition stage failed: " + module)
        report["status"] = "GREEN"
    except Exception as error:
        report.update(
            status="FAILED", error_type=type(error).__name__, error=str(error)
        )
    finally:
        save_json(output / "composition-result.json", report)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--page-trial", type=Path, required=True)
    parser.add_argument("--page", default="registration")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--budget", type=Path, required=True)
    parser.add_argument("--checkpoints", type=Path, required=True)
    args = parser.parse_args()
    result = run(
        args.base,
        args.page_trial,
        args.output,
        args.page,
        args.budget,
        args.checkpoints,
    )
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "GREEN" else 1)
