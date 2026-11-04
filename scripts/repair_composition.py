"""Repair one generated page in a diagnostic copy, retaining frozen regressions."""

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "compiler"), str(ROOT / "scripts")]
from stage_replay import fingerprint
from infrastructure.shared.agent.checkpoints import capture, restore
from infrastructure.shared.agent.context import SourceFiles
from infrastructure.shared.agent.files import FileWorkspace
from infrastructure.shared.agent.frozen_tests import freeze_tests, verify_frozen_tests
from infrastructure.shared.agent.loop import run_file_agent
from infrastructure.shared.models.text import TextModel
from infrastructure.stages.backend.testing import (
    BackendChecks,
    require_green as backend_green,
)
from infrastructure.stages.frontend.context import load_ui_context
from infrastructure.stages.frontend.triggers.testing import E2EChecks
from infrastructure.stages.frontend.ui.contracts import (
    control_contract,
    radio_group_suite,
)
from infrastructure.stages.frontend.ui.testing import FrontendChecks, require_green
from infrastructure.utils.files import save_json
from infrastructure.utils.presentation.console import DemoConsole
from infrastructure.utils.presentation.logging import console_log


def repair(source, output, ledger):
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    os.environ.setdefault("MODEL", "deepseek-flash")
    os.environ["ARC_EXPERIMENT_BUDGET"] = str(Path(ledger).resolve())
    os.environ["MAX_OUTPUT_TOKENS"] = str(
        json.loads(Path(ledger).read_text())["max_output_tokens"]
    )
    source, output = Path(source).resolve(), Path(output).resolve()
    if not output.is_relative_to(ROOT / "work"):
        raise ValueError("Repair copy must be under repository work/")
    checkpoint = output.with_name(output.name + "-source")
    capture(source, checkpoint)
    restore(checkpoint, output)
    shutil.copytree(source / "node_modules", output / "node_modules", symlinks=True)
    tree, _, contexts = load_ui_context(output / ".arc", ROOT / "input")
    contracts = [
        control_contract(requirement) for requirement in tree.requirements.values()
    ]
    relative = "frontend/tests/ui/requirement-radio-groups.spec.ts"
    suite = radio_group_suite(contracts)
    (output / relative).write_text(suite)
    freeze_tests(output, [relative])
    index = json.loads((output / ".arc/implementation_paths.json").read_text())
    ui_files = sorted(
        p.relative_to(output).as_posix()
        for p in (output / "frontend/tests/ui").glob("*.spec.ts")
    )
    e2e_files = list(index["e2e_test"].values())
    api_files = list(index["backend_test"].values())
    backend = BackendChecks(output)
    backend.http_apis = json.loads((output / ".arc/backend_apis.json").read_text())[
        "apis"
    ]
    ui, e2e = FrontendChecks(output), E2EChecks(output)
    checks = {}

    def gate():
        nonlocal checks
        checks = {
            "typecheck": ui.typecheck(ui_files),
            "backend_typecheck": backend.typecheck(),
            "ui": ui.tests(ui_files),
            "e2e": e2e.tests(e2e_files),
            "backend_tests": backend.tests(api_files),
            "build": ui.build(),
        }
        save_json(output / "repair-checks.json", checks)
        for key in ("typecheck", "backend_typecheck", "build"):
            if checks[key]["returncode"]:
                raise ValueError(f"{key}: {checks[key]['output']}")
        require_green(checks["ui"])
        require_green(checks["e2e"])
        backend_green(checks["backend_tests"])
        verify_frozen_tests(output)
        return checks

    report = {
        "kind": "diagnostic page repair, not complete generation",
        "complete_generation": False,
        "status": "FAILED",
        "source": str(source),
        "compiler_files": fingerprint(),
        "additive_suite_sha256": sha256(suite.encode()).hexdigest(),
    }
    with console_log(
        output, stage="Named radio-group repair and full regressions", model_log=True
    ):
        initial = ui.tests([relative])
        report["negative_control"] = {k: v for k, v in initial.items() if k != "output"}
        if initial["returncode"] == 0 or not initial.get("failed"):
            raise ValueError(
                "Expected meaningful named-group assertion failure before repair"
            )
        target = index["page"]["registration"]
        workspace = FileWorkspace(
            output,
            [target],
            references=[
                relative,
                "frontend/tests/ui/registration.spec.ts",
                "frontend/src/ui-runtime.ts",
            ],
        )
        selection = SourceFiles(output)
        task = {
            "requirement": contexts["REQ-2"],
            "source_control_contract": control_contract(contexts["REQ-2"]),
            "implementation_path": target,
            "observed_issue": "The named single-choice field has real radio options but its container exposes generic group semantics. Preserve individual option names and existing behavior; repair the accessible named radiogroup.",
        }
        try:
            result = run_file_agent(
                TextModel(),
                "Repair only the supplied registration page's native radio-group accessibility semantics. Preserve all source IDs, state bindings, events, visual structure and business behavior. The original requirement names the group and its options. Do not change tests or add unrelated code.",
                task,
                workspace,
                gate,
                max_turns=1,
                console=DemoConsole(False),
                label="Named radio group",
                feedback=initial,
                feedback_filter=lambda value: selection.feedback(workspace, value),
            )
            report.update(status="GREEN", turns=result["turns"])
        except Exception as error:
            report.update(error_type=type(error).__name__, error=str(error))
        # Publish only results freshly earned by this exact repaired application.
        if report["status"] == "GREEN":
            previous_ui = json.loads((source / ".arc/ui_checks.json").read_text())
            previous_e2e = json.loads((source / ".arc/frontend_e2e.json").read_text())
            previous_ui.update(
                status="GREEN",
                verification={
                    "typecheck": {"status": "GREEN", "result": checks["typecheck"]},
                    "tests": {"status": "GREEN", "result": checks["ui"]},
                    "build": {"status": "GREEN", "result": checks["build"]},
                },
            )
            previous_ui["summary"] = {
                "pages": 3,
                "tests": checks["ui"]["passed"],
                "failed": 0,
            }
            previous_e2e.update(
                status="GREEN",
                verification={
                    key: {"status": "GREEN", "result": value}
                    for key, value in checks.items()
                },
            )
            previous_e2e["summary"].update(
                ui_tests=checks["ui"]["passed"],
                e2e_tests=checks["e2e"]["passed"],
                failed=0,
            )
            save_json(output / ".arc/ui_checks.json", previous_ui)
            save_json(output / ".arc/frontend_e2e.json", previous_e2e)
            save_json(
                output / ".arc/backend_tdd.json",
                {
                    "status": "GREEN",
                    "kind": "fresh repair regression",
                    "verification": {
                        key: {"status": "GREEN", "result": checks[key]}
                        for key in ("backend_typecheck", "backend_tests", "build")
                    },
                },
            )
    save_json(output / "repair-result.json", report)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--budget", type=Path, required=True)
    args = parser.parse_args()
    result = repair(args.source, args.output, args.budget)
    print(
        json.dumps({k: v for k, v in result.items() if k != "compiler_files"}, indent=2)
    )
    raise SystemExit(0 if result["status"] == "GREEN" else 1)
