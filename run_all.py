"""Run tutorial steps 00 through 12 sequentially without teaching pauses."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

from infrastructure.utils.cli import COMPILER_DIR, resolve_directories
from infrastructure.utils.processes import start_process, stop_process
from infrastructure.utils.presentation.logging import configure_console
from infrastructure.utils.presentation.console import show_panel
from infrastructure.utils.presentation.stages import stage_label


STEPS = (
    "00_project_initialization.py",
    "01_explore_requirement.py",
    "02_build_db_schema.py",
    "03_infer_db_obligations.py",
    "04_check_db_obligations.py",
    "05_implement_db.py",
    "06_decompose_backend_apis.py",
    "07_infer_api_contracts.py",
    "08_implement_backend_tdd.py",
    "09_design_ui.py",
    "10_implement_ui.py",
    "11_design_ui_interactions.py",
    "12_implement_frontend_tdd.py",
)

# Artifacts that prove a step already finished. Steps with no sentinel are
# always rerun (they are cheap, self-resuming or act as pure checkers).
SENTINELS = {
    "00_project_initialization.py": ("package.json",),
    "01_explore_requirement.py": (".arc/requirements.json", ".arc/visual_analysis.json"),
    "02_build_db_schema.py": (".arc/db_schema.json",),
    "03_infer_db_obligations.py": (".arc/db_obligations.json",),
    "04_check_db_obligations.py": (),
    "05_implement_db.py": (),  # 哨兵在 step_completed 特判：tables 目录须含至少一个 .sql
    "06_decompose_backend_apis.py": (".arc/backend_apis.json",),
    "07_infer_api_contracts.py": (".arc/backend_contracts.json",),
    "08_implement_backend_tdd.py": (".arc/backend_tdd.json",),
    "09_design_ui.py": (),
    "10_implement_ui.py": (".arc/ui_checks.json",),
    "11_design_ui_interactions.py": (".arc/ui_interactions.json",),
    "12_implement_frontend_tdd.py": (".arc/frontend_e2e.json",),
}

# Steps whose sentinel must additionally report status GREEN to count as done.
GREEN_SENTINELS = {
    "08_implement_backend_tdd.py": ".arc/backend_tdd.json",
    "12_implement_frontend_tdd.py": ".arc/frontend_e2e.json",
}


def step_completed(output: Path, step: str) -> bool:
    """True when every sentinel artifact exists (and reports GREEN where required)."""
    if step == "05_implement_db.py":
        # The scaffold creates an empty backend/src/db/tables directory; stage 05
        # is only complete when at least one generated .sql table lives in it.
        tables = output / "backend/src/db/tables"
        return tables.is_dir() and any(tables.glob("*.sql"))
    sentinels = SENTINELS.get(step, ())
    if not sentinels or not all((output / relative).exists() for relative in sentinels):
        return False
    green_path = GREEN_SENTINELS.get(step)
    if green_path is None:
        return True
    try:
        return json.loads((output / green_path).read_text(encoding="utf-8-sig")).get("status") == "GREEN"
    except (OSError, ValueError):
        return False


def main() -> None:
    configure_console()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=COMPILER_DIR / "input", help="Requirement/image directory")
    parser.add_argument("--output", type=Path, required=True, help="Shared output directory for all steps")
    parser.add_argument("--resume", action="store_true",
        help="Skip steps whose artifacts already exist (08/12 additionally require status GREEN)")
    args = parser.parse_args()
    try:
        input_dir, output_dir = resolve_directories(args)
        if not input_dir.is_dir():
            raise ValueError(f"Input directory does not exist: {input_dir}")
        show_panel("Requirement compiler | Pipeline", f"Input: {input_dir}\nOutput: {output_dir}\nStages to run: {len(STEPS)}\nResume: {args.resume}")
        for index, step in enumerate(STEPS, 1):
            if args.resume and step_completed(output_dir, step):
                show_panel(f"[{index}/{len(STEPS)}] {stage_label(step)}", "Artifacts already complete; skipping (--resume).")
                continue
            show_panel(f"[{index}/{len(STEPS)}] {stage_label(step)}", f"Running {step}")
            command = [sys.executable, str(COMPILER_DIR / step), "--input", str(input_dir), "--output", str(output_dir)]
            if step == "01_explore_requirement.py":
                command.append("--no-browse")
            process = start_process(
                command,
                cwd=COMPILER_DIR,
            )
            try:
                code = process.wait()
            except BaseException:
                stop_process(process)
                raise
            if code:
                raise subprocess.CalledProcessError(code, [sys.executable, step])
    except subprocess.CalledProcessError as error:
        parser.exit(error.returncode if error.returncode > 0 else 1, f"Pipeline stopped: {step} failed.\n")
    except (OSError, ValueError) as error:
        parser.exit(1, f"Execution failed: {error}\n")
    except KeyboardInterrupt:
        parser.exit(130, "Pipeline interrupted.\n")
    show_panel("[DONE] All steps completed", f"Output: {output_dir}", tone="success")


if __name__ == "__main__":
    main()
