"""Audited task replay and explicit stage windows; no implicit trusted resume."""

import argparse
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from importlib import import_module
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "compiler"), str(ROOT / "scripts")]
from context_audit import request_records
from infrastructure.shared.agent.checkpoints import capture, restore
from infrastructure.stages.frontend.ui.contracts import control_contract
from infrastructure.stages.frontend.ui.design import apply_proposal, empty_design
from infrastructure.stages.requirements.tree import RequirementTree
from infrastructure.utils.presentation.logging import console_log


def fresh(path):
    path = Path(path).expanduser().resolve()
    if not path.is_relative_to(ROOT / "work"):
        raise ValueError("Experiment output must be under repository work/")
    path.mkdir(parents=True, exist_ok=False)
    return path


def fingerprint():
    return {
        p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()).hexdigest()
        for folder in (ROOT / "compiler", ROOT / "input", ROOT / "scripts")
        for p in sorted(folder.rglob("*"))
        if p.is_file() and "__pycache__" not in p.parts and p.name != ".env"
    }


def budget(path, calls=6, tokens=120000, seconds=900):
    if min(calls, tokens, seconds) < 1:
        raise ValueError("Budget limits must be positive")
    record = {
        "max_calls": calls,
        "max_tokens": tokens,
        "max_output_tokens": 12000,
        "calls": 0,
        "total_tokens": 0,
        "pending": False,
        "unknown_usage": False,
        "deadline_utc": (
            datetime.now(timezone.utc) + timedelta(seconds=seconds)
        ).isoformat(),
        "scope": "Serial experiment; check known usage before calls; not a billing cap",
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(record, stream, indent=2)
        stream.write("\n")
    return record


def replay(log, call_id, variant, output, ledger, repair_from=None):
    """Replay one UI design proposal from its exact audited request; no auto repair."""
    log = Path(log).resolve()
    records = list(request_records(log))
    record = next((r for r in records if r["call_id"] == call_id), None)
    if not record or "Stage 09" not in record["stage"]:
        raise ValueError("Select one audited Stage 09 UI design request")
    output = fresh(output)
    request = json.loads(json.dumps(record["arguments"]))
    payload = json.loads(request["messages"][-1]["content"])
    if variant == "contract":
        payload["control_contract"] = control_contract(payload["requirement"])
        request["messages"][-1]["content"] = json.dumps(payload, ensure_ascii=False)
    request.pop("max_tokens", None)
    request.pop("max_completion_tokens", None)
    request["max_completion_tokens"] = 12000
    (output / "request.json").write_text(json.dumps(request, indent=2) + "\n")
    metadata = {
        "kind": "single UI design task replay",
        "variant": variant,
        "historical_call_id": call_id,
        "source_log_sha256": sha256(log.read_bytes()).hexdigest(),
        "request_sha256": sha256((output / "request.json").read_bytes()).hexdigest(),
        "source_files": fingerprint(),
        "budget": str(Path(ledger).resolve()),
        "complete_generation": False,
    }
    (output / "identity.json").write_text(json.dumps(metadata, indent=2) + "\n")
    # Rebuild only earlier accepted UI design proposals, not later final artifacts.
    tree = RequirementTree(
        json.loads((log.parent / ".arc/requirements.json").read_text())
    )
    design = empty_design()
    pending = None
    for line in log.open():
        item = json.loads(line)
        if item.get("event") == "request":
            if item["call_id"] == call_id:
                break
            pending = item if "Stage 09" in item.get("stage", "") else None
        elif (
            item.get("event") == "response"
            and pending
            and item["call_id"] == pending["call_id"]
        ):
            earlier = json.loads(pending["arguments"]["messages"][-1]["content"])
            proposal = json.loads(item["response"]["choices"][0]["message"]["content"])
            design = apply_proposal(
                design, proposal, earlier["requirement"]["id"], tree
            )
            pending = None
    if repair_from:
        from infrastructure.shared.agent.proposals import REPAIR_INSTRUCTIONS

        previous_root = Path(repair_from).resolve()
        previous_identity = json.loads((previous_root / "identity.json").read_text())
        if (
            previous_identity["historical_call_id"] != call_id
            or previous_identity["source_log_sha256"] != metadata["source_log_sha256"]
        ):
            raise ValueError("Repair input must belong to this exact historical task")
        previous = json.loads((previous_root / "response.json").read_text())
        rejected = json.loads(previous["choices"][0]["message"]["content"])
        try:
            apply_proposal(design, rejected, payload["requirement"]["id"], tree)
        except ValueError as error:
            payload["correction"] = {"error": str(error), "previous_response": rejected}
        else:
            raise ValueError(
                "Previous proposal already passes; no repair request is needed"
            )
        request["messages"][0]["content"] += "\n\n" + REPAIR_INSTRUCTIONS
        request["messages"][-1]["content"] = json.dumps(payload, ensure_ascii=False)
        metadata["repair_from"] = str(previous_root)
        (output / "request.json").write_text(json.dumps(request, indent=2) + "\n")
        metadata["request_sha256"] = sha256(
            (output / "request.json").read_bytes()
        ).hexdigest()
        (output / "identity.json").write_text(json.dumps(metadata, indent=2) + "\n")
    os.environ["ARC_EXPERIMENT_BUDGET"] = str(Path(ledger).resolve())
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    os.environ.setdefault("MODEL", request["model"])
    from infrastructure.shared.models.text import TextModel
    from infrastructure.utils.presentation.model_io import invoke

    model = TextModel(json_mode=False)
    if request["model"] != model.name:
        raise ValueError(
            "Replay model must match historical request; set MODEL explicitly"
        )
    status = {"status": "FAILED", "complete_generation": False}
    with console_log(output, stage="UI design context replay", model_log=True):
        try:
            response = invoke(model.client, request)
            raw = response.model_dump(mode="json")
            (output / "response.json").write_text(json.dumps(raw, indent=2) + "\n")
            if (
                not raw.get("choices")
                or raw["choices"][0].get("finish_reason") == "length"
            ):
                raise ValueError("Missing or truncated response; no automatic retry")
            proposal = json.loads(raw["choices"][0]["message"]["content"])
            updated = apply_proposal(
                design, proposal, payload["requirement"]["id"], tree
            )
            (output / "ui_design.json").write_text(json.dumps(updated, indent=2) + "\n")
            status.update(status="GREEN", usage=raw.get("usage"))
        except Exception as error:
            status.update(error_type=type(error).__name__, error=str(error))
    (output / "result.json").write_text(json.dumps(status, indent=2) + "\n")
    return status


def page_replay(trial, page_id, output, ledger, dependencies):
    """Implement one accepted design page in a fresh scaffold, with actual browser gates."""
    from copy import deepcopy
    import shutil
    from infrastructure.shared.project.initialize import initialize_project
    from infrastructure.shared.models.text import TextModel
    from infrastructure.stages.frontend.ui.design import page_elements
    from infrastructure.stages.frontend.ui.implementation import implement_ui
    from infrastructure.utils.presentation.console import DemoConsole
    from dotenv import load_dotenv

    trial = Path(trial).resolve()
    if json.loads((trial / "result.json").read_text())["status"] != "GREEN":
        raise ValueError("Page replay requires an accepted design trial")
    design = deepcopy(json.loads((trial / "ui_design.json").read_text()))
    elements = page_elements(design, page_id)
    design["pages"] = {page_id: design["pages"][page_id]}
    design["elements"] = elements
    for key in ("requirements", "steps"):
        design[key] = {
            identity: [uid for uid in ids if uid in elements]
            for identity, ids in design[key].items()
        }
    route = design["pages"][page_id]["route"]
    design["control_contracts"] = {
        rid: contract
        for rid, contract in design.get("control_contracts", {}).items()
        if contract["route"] == route
    }
    request = json.loads((trial / "request.json").read_text())
    requirement = json.loads(request["messages"][-1]["content"])["requirement"]
    output = fresh(output)
    initialize_project(output)
    shutil.copytree(
        Path(dependencies).resolve(), output / "node_modules", symlinks=True
    )
    os.environ["ARC_EXPERIMENT_BUDGET"] = str(Path(ledger).resolve())
    os.environ["MAX_OUTPUT_TOKENS"] = "12000"
    load_dotenv(ROOT / ".env")
    os.environ.setdefault("MODEL", request["model"])
    identity = {
        "kind": "single page implementation",
        "complete_generation": False,
        "design_trial": str(trial),
        "design_sha256": sha256((trial / "ui_design.json").read_bytes()).hexdigest(),
        "page": page_id,
        "source_files": fingerprint(),
    }
    (output / "identity.json").write_text(json.dumps(identity, indent=2) + "\n")
    report = {"status": "RUNNING", "pages": {}}
    with console_log(output, stage="Single page implementation replay", model_log=True):
        try:
            implement_ui(
                output / ".arc",
                design,
                TextModel(),
                DemoConsole(False),
                report,
                max_turns=2,
                images=requirement.get("images", {}),
                requirement_contexts={requirement["id"]: requirement},
            )
        except Exception as error:
            report.update(
                status="FAILED", error_type=type(error).__name__, error=str(error)
            )
    report["complete_generation"] = False
    (output / "result.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def window(checkpoint, output, inputs, start, end, ledger, dependencies=None):
    """Execute 09–12 (or a subwindow) from explicit artifacts, earning new stage results."""
    if not 9 <= start <= end <= 12:
        raise ValueError("Supported stage window: 09 through 12")
    output = Path(output).resolve()
    if not output.is_relative_to(ROOT / "work") or output.exists():
        raise ValueError("Choose a new output under work/")
    if not Path(ledger).is_file():
        raise ValueError("Initialize a shared experiment budget first")
    checkpoint_record = json.loads((Path(checkpoint) / "checkpoint.json").read_text())
    if not str(checkpoint_record.get("stage", "")).startswith(f"{start:02d}_"):
        raise ValueError(
            "Stage window requires a checkpoint captured before its named starting stage; manual/final snapshots are diagnostic only"
        )
    restore(checkpoint, output)
    if dependencies:
        (output / "node_modules").symlink_to(
            Path(dependencies).resolve(), target_is_directory=True
        )
    os.environ["ARC_EXPERIMENT_BUDGET"] = str(Path(ledger).resolve())
    os.environ["MAX_OUTPUT_TOKENS"] = "12000"
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    os.environ.setdefault("MODEL", "deepseek-flash")
    stages = {
        9: ("09_design_ui", "design_frontend_ui"),
        10: ("10_implement_ui", "implement_frontend_ui"),
        11: ("11_design_frontend_triggers", "design_frontend_triggers"),
        12: ("12_implement_frontend_tdd", "implement_frontend_triggers"),
    }
    report = {
        "kind": "stage window",
        "complete_generation": False,
        "stages": {},
        "status": "RUNNING",
        "source_files": fingerprint(),
        "checkpoint_sha256": sha256(
            (Path(checkpoint) / "checkpoint.json").read_bytes()
        ).hexdigest(),
    }
    try:
        for number in range(start, end + 1):
            module, function = stages[number]
            with console_log(output, stage=module, model_log=True):
                options = {"max_attempts": 2} if number in {9, 11} else {"max_turns": 2}
                result = getattr(import_module(module), function)(
                    Path(inputs).resolve(), output / ".arc", **options
                )
            report["stages"][module] = result.get("status", "GREEN")
            if report["stages"][module] not in {"GREEN", "NO_UI"}:
                raise ValueError("Stage did not pass: " + module)
        report["status"] = "GREEN"
    except (ValueError, RuntimeError) as error:
        report.update(status="FAILED", error=str(error))
    finally:
        (output / "stage-window.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("budget")
    p.add_argument("output", type=Path)
    p.add_argument("--calls", type=int, default=6)
    p.add_argument("--tokens", type=int, default=120000)
    p.add_argument("--seconds", type=int, default=900)
    p = sub.add_parser("snapshot")
    p.add_argument("application", type=Path)
    p.add_argument("--output", type=Path, required=True)
    p = sub.add_parser("task")
    p.add_argument("log", type=Path)
    p.add_argument("--call-id", required=True)
    p.add_argument("--variant", choices=("original", "contract"), required=True)
    p.add_argument("--repair-from", type=Path)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--budget", type=Path, required=True)
    p = sub.add_parser("page")
    p.add_argument("trial", type=Path)
    p.add_argument("--page", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--budget", type=Path, required=True)
    p.add_argument("--dependencies", type=Path, required=True)
    p = sub.add_parser("window")
    p.add_argument("checkpoint", type=Path)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--input", type=Path, default=ROOT / "input")
    p.add_argument("--from-stage", type=int, default=9)
    p.add_argument("--to-stage", type=int, default=12)
    p.add_argument("--budget", type=Path, required=True)
    p.add_argument("--dependencies", type=Path)
    args = parser.parse_args()
    if args.command == "budget":
        result = budget(args.output, args.calls, args.tokens, args.seconds)
    elif args.command == "snapshot":
        destination = args.output.resolve()
        if not destination.is_relative_to(ROOT / "work"):
            parser.error("Checkpoint output must be under work/")
        result = capture(args.application, destination)
    elif args.command == "task":
        result = replay(
            args.log,
            args.call_id,
            args.variant,
            args.output,
            args.budget,
            args.repair_from,
        )
    elif args.command == "page":
        result = page_replay(
            args.trial, args.page, args.output, args.budget, args.dependencies
        )
    else:
        result = window(
            args.checkpoint,
            args.output,
            args.input,
            args.from_stage,
            args.to_stage,
            args.budget,
            args.dependencies,
        )
    print(
        json.dumps(
            {k: v for k, v in result.items() if k not in {"files", "source_files"}},
            indent=2,
        )
    )
    return 0 if result.get("status", "GREEN") == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
