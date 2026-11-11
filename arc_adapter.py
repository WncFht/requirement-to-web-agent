"""ARC-Bench file/CLI adapter for upstream mini-swe-agent v2.4.6.

No changes to DefaultAgent, LitellmModel, or LocalEnvironment. Harness prompts and
limits are adopted verbatim from the shipped configs (benchmarks/swebench.yaml for
the tool-calling contract, default.yaml for shell env); this adapter only carries
task-domain content.
"""

from __future__ import annotations

import base64
import importlib.resources
import json
import mimetypes
import os
import shutil
import time
from pathlib import Path
from typing import Any

import yaml

from progress import (
    BashProgress,
    ModelProgress,
    elide_images,
    emit,
    exception_chain,
    redact,
    variable_presence,
)

# Keep stdout a pure JSON event stream: no upstream banner, no litellm provider list.
os.environ.setdefault("MSWEA_SILENT_STARTUP", "1")

BASE = Path(__file__).resolve().parent
TEMPLATE = BASE / "web_template"
MULTIMODAL_REGEX = r"(?s)<MSWEA_MULTIMODAL_CONTENT><CONTENT_TYPE>(.+?)</CONTENT_TYPE>(.+?)</MSWEA_MULTIMODAL_CONTENT>"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
IMAGE_MAX_SIDE = 1280
IMAGE_JPEG_QUALITY = 82


def inspect_input(input_dir: Path) -> dict[str, Any]:
    """Check input, but never rewrite or flatten the source requirements."""
    src = input_dir / "requirements.yaml"
    if not src.is_file():
        raise ValueError(f"Missing requirements.yaml: {src}")
    raw = src.read_text(encoding="utf-8-sig")
    if not isinstance(yaml.safe_load(raw), dict):
        raise ValueError("requirements.yaml must contain a YAML mapping")
    reference = input_dir / "reference"
    images = (
        sorted(
            (
                p
                for p in reference.rglob("*")
                if p.is_file() and p.suffix.lower() in IMAGE_EXTS
            ),
            key=lambda p: str(p.relative_to(input_dir)),
        )
        if reference.exists()
        else []
    )
    return {"raw_yaml": raw, "images": images}


def prepare_output(input_dir: Path, output_dir: Path) -> dict[str, Any]:
    input_dir, output_dir = input_dir.resolve(), output_dir.resolve()
    if (
        input_dir == output_dir
        or input_dir in output_dir.parents
        or output_dir in input_dir.parents
    ):
        raise ValueError("Input and output directories must not contain each other")
    checked = inspect_input(input_dir)
    # Like version2: the runner may have already created logs or a template.
    # Fill missing infrastructure without replacing runner/application files.
    output_dir.mkdir(parents=True, exist_ok=True)
    for source in sorted(TEMPLATE.rglob("*")):
        if not source.is_file() or source.name == ".DS_Store":
            continue
        target = output_dir / source.relative_to(TEMPLATE)
        if not target.resolve().is_relative_to(output_dir):
            raise ValueError(f"Template path escapes output: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            with target.open("xb") as stream:
                stream.write(source.read_bytes())
            shutil.copymode(source, target)
        except FileExistsError:
            if not target.is_file():
                raise ValueError(f"Expected project file: {target}")
    # Keep all supplied assets (including unrecognized asset types) accessible to the agent.
    staging = output_dir / ".arc_requirements"
    shutil.copytree(input_dir, staging, dirs_exist_ok=True)
    return checked


def _slim_image(path: Path, max_side: int = IMAGE_MAX_SIDE) -> tuple[bytes, str] | None:
    """Downscale and re-encode one image (JPEG/PNG, whichever encodes smaller).

    Returns None when Pillow is unavailable or the file cannot be decoded;
    the caller then attaches the original bytes.
    """
    try:
        from io import BytesIO

        from PIL import Image
    except ImportError:
        return None
    try:
        with Image.open(path) as im:
            rgb = im.convert("RGB")
            width, height = rgb.size
            scale = max_side / max(width, height)
            if scale < 1:
                rgb = rgb.resize(
                    (max(1, round(width * scale)), max(1, round(height * scale))),
                    Image.Resampling.LANCZOS,
                )
            best: tuple[bytes, str] | None = None
            for fmt, media in (("JPEG", "image/jpeg"), ("PNG", "image/png")):
                buffer = BytesIO()
                rgb.save(
                    buffer, format=fmt, quality=IMAGE_JPEG_QUALITY
                )  # PNG ignores quality
                encoded = buffer.getvalue()
                if best is None or len(encoded) < len(best[0]):
                    best = (encoded, media)
            return best
    except Exception as exc:  # malformed image: fall back to the original bytes
        emit(
            "image_slim_error",
            file=path.name,
            exception=type(exc).__name__,
            message=str(exc)[:120],
        )
        return None


def _attach_image(path: Path) -> tuple[bytes, str, bool]:
    """(payload, media, slimmed): slimmed attachment with original-bytes fallback."""
    slim = _slim_image(path)
    if slim is None:
        return (
            path.read_bytes(),
            mimetypes.guess_type(path.name)[0] or "image/png",
            False,
        )
    return slim[0], slim[1], True


def _image_part(payload: bytes, media: str) -> str:
    encoded = base64.b64encode(payload).decode("ascii")
    return (
        "<MSWEA_MULTIMODAL_CONTENT><CONTENT_TYPE>image_url</CONTENT_TYPE>"
        f"data:{media};base64,{encoded}</MSWEA_MULTIMODAL_CONTENT>"
    )


# Harness contract, adapted from the shipped tool-calling benchmark config
# (minisweagent 2.4.6 config/benchmarks/swebench.yaml): only the Overview, Boundaries,
# Workflow and Submission sections carry ARC-Bench wording; everything else is upstream text.
UPSTREAM_INSTANCE_SKELETON = """<requirements>
Consider the following task specification:
{{task}}
</requirements>

<instructions>
# Task Instructions

## Overview

Implement the ENTIRE application described by the supplied requirements and visual references
in the current workspace. Completion means working user journeys with successful self-tests
on the final source, not merely code written, pages present, or a successful build.
Use the existing template and preserve working behavior. Work through actual bash tool calls:
inspect, implement, execute tests, diagnose failures, repair, and retest until complete.
Each response must include a brief THOUGHT explaining the next concrete action and at least
one bash tool call. Keep reasoning focused on implementation and evidence.

## Important Boundaries

- Modify application source and add requirement-derived self-tests as needed. Preserve
  `deploy.sh`, supplied tests/assertions and their harness, and `.arc_requirements/` unchanged.
- Use supplied public requirements, assets, application source, installed dependencies and
  ordinary dependency documentation. Do not search for external evaluator tests, platform
  submission internals, benchmark answers, or other runs. Existing application tests are usable.
- `.arc_adapter/` and `.arc/stdout.log` are audit artifacts, not task input. If present,
  `.arc/preflight.json` may be read for environment capabilities; it is not acceptance evidence.
- Implement general behavior. Do not special-case known scenario titles, account names or
  fixture values to produce answers. Do not change assertions to conceal unmet requirements.

## Recommended Workflow

### 1. Build a coverage map, then start implementing

Read the supplied YAML hierarchy and references. Child requirements inherit applicable parent
constraints. Preserve original IDs and cover every scenario, including negative cases and
alternatives. Written behavior, required messages, roles, names, defaults, identity and starting
context are contracts; screenshots also guide visual layout. Resolve unspecified details with
simple choices consistent with the application rather than inventing additional scope.

Maintain a compact local coverage map keyed by requirement/scenario ID. For each scenario,
record its GIVEN page/identity/data, WHEN actions, THEN assertions, test file/case and result
(not_run, failed, passed). If no scenario IDs exist, use the requirement ID and a short case name.
Passed means an executed case met ALL its assertions on the relevant source. Printing a label,
creating a test file, or editing a shared component does not verify its dependent scenarios.
Keep this map concise and update it as work proceeds; do not spend the run writing a report
or designing a new test framework before implementing the application.

Inspect package scripts and relevant UI, routes, API and persistence. Order features by real
prerequisites and shared resources, establishing essential navigation, identity and data flow
first. Implement related functionality in manageable groups while tracking coverage of the
whole application. Complete UI, business rules and storage together; avoid a broad collection
of disconnected placeholder pages or polishing one area while other required areas are absent.

### 2. Implement complete journeys and business state

For every scenario implement the entire path:
specified page and identity -> visible entry -> interaction -> observable result -> required
persistence. A direct route, API response, success toast or database schema alone is insufficient.

- Provide explicitly required GIVEN records and relationships through normal, idempotent
  initialization/migrations. Preserve existing data and IDs; restarts must not overwrite edits.
  In tests, create case-isolated data through normal user actions where the scenario requires it.
- Keep write requests, stored fields, read responses and frontend state consistent. Verify that
  reload/reopen reconstructs the result and a subsequent ordinary edit preserves other state.
  Use the persistence mechanism the requirement specifies; browser state cannot replace
  required shared or account-specific backend data.
- Await the relevant write before announcing durable success. Show real save errors. Guard
  initial loads, queued writes and delayed responses so stale snapshots cannot overwrite new
  records, edits or newer navigation. Do not let startup backfills bypass live creation logic.
- Model required transitions explicitly: draft versus published, selected versus confirmed,
  unpaid versus paid/cancelled, active versus archived/deleted. Confirm commits once; decline
  or cancel preserves the prior state. Refresh/reopen must agree with the committed transition.
- Keep related business values consistent: selected entity/variant, quantity, price, totals,
  availability and resulting record. Validate limits and required fields before committing;
  rejected actions must not create records or partially change balances, stock or membership.
- Enforce ownership and permissions on backend reads/writes as well as UI controls. Test a
  second account or anonymous session where the requirements specify isolation or restrictions.
  Public views expose only allowed data; another user's private records must not leak.

Apply these rules to the actual requirements. Do not add unrelated product features, arbitrary
validation, fixed dates or historical seed data that the task does not request.

### 3. Treat accessibility semantics as executable contracts

For each specified role/name, verify the actual accessible name and role, not just visible text.
Use semantic controls, associated labels and accurate expanded, selected, checked, pressed,
current and disabled states. Supply explicit accessible names where native semantics do not
provide the required name. Decorative icons, punctuation or CSS-generated text must not change
it. A notification showing text is not necessarily a status named by that text.

In browser checks, use `getByRole(role, { name, exact: true })`, scoped to the required container.
Assert uniqueness and visibility where one control is required, then its state and behavior.
For example, when the requirement specifies a status named "Saved", verify the named status:

```javascript
const saved = page.getByRole('status', { name: 'Saved', exact: true });
await expect(saved).toHaveCount(1);
await expect(saved).toBeVisible();
```

Visible text, an accessible name, an input value and an accessible description are different
properties; assert the property the requirement specifies. Scope repeated actions to their
business record or dialog. Do not use `.first()`, `.nth()` or broad text matching to hide an
ambiguous required control. Index selection is appropriate only when order itself is specified.
If a locator is wrong, correct it against the public requirement; if the UI is wrong, repair it.

### 4. Write self-tests that actually fail

Use the installed browser tooling and its assertion library, or equivalent assertions that
throw on mismatch. Reuse small helpers for recurring interactions; keep tests tied to scenario
IDs and retain them in the application workspace for reruns. Do not duplicate supplied suites.

- Assert every THEN outcome, including exact required messages, validation, negative cases,
  selected state and persistence. `console.log(count)`, screenshots, printed PASS/FAIL and
  reaching the end of a script are diagnostics, not assertions. Zero matches, false conditions,
  unexpected response statuses and browser exceptions must fail their relevant checks.
- If collecting multiple failures, continue independent cases but finish with a nonzero exit
  whenever any case failed. A catch block must not swallow the failure. Use the test runner's
  failure status, or throw/set `process.exitCode = 1` after reporting collected failures.
  Run all planned cases; an early script exception leaves later cases not_run, not passed.
- Scope response checks to the operation: assert its expected success or rejection status and
  resulting UI/data. An intentionally rejected negative case is not an unexpected HTTP error;
  unrelated console output alone also does not prove success or failure.
- Verify the assertion runner itself with a temporary deliberately failing assertion before
  relying on a new self-test setup. Confirm it returns nonzero, then remove that probe.
- Preserve actual command status. For checks piped through `tee` or `tail`, use
  `bash -o pipefail -c 'node path/to/check.cjs 2>&1 | tee /tmp/check.log'`, or redirect output,
  capture `$?` immediately, print the relevant log, and exit with the captured status.
  Later successful commands, log printing, `|| true` or an echo must not mask test failure.

### 5. Exercise real entry paths, persistence and timing

Start browser verification at each scenario's specified GIVEN page and identity, then use its
actual navigation and controls. A direct URL, API call, hand-edited database or forced browser
state may diagnose a problem but cannot verify a missing entry or replace a required action.
Use records' full business identities so one entity's result cannot satisfy another's case.

- Run each scenario independently with isolated browser/session state and its prescribed data.
  Use a disposable application/database copy for destructive self-tests. Resetting a disposable
  test fixture is allowed; clearing the working database to obtain a pass is not.
- Check shared entry points early. After changing authentication, navigation, forms or storage,
  rerun the affected groups. A shared entry failure can block many scenarios: repair that cause,
  then execute the downstream assertions before marking those scenarios passed.
- Exercise create -> read -> edit -> reopen paths, combinations of filters, and required
  confirmation/decline branches. For multi-step flows, check backward/reopen behavior and the
  final record, not just advancement to the next page. Test required reload, restart and account
  switching rather than assuming a successful write proves persistence or isolation.
- Use auto-retrying assertions and wait for specific visible states or acknowledged operations.
  Do not rely on fixed sleeps or universally wait for networkidle to make the app usable.
  Test immediate interaction with available controls during cold loading and consecutive
  save/navigation actions; delayed initialization must not erase newer work.
- For timing-sensitive changes, test the relevant response ordering, for example with controlled
  network delay in a disposable browser test. Fix stale updates and operation ownership rather
  than adding sleeps, extra navigation or longer timeouts that conceal the defect.
- Verify layout and required visual states against the references as well as functionality.
  A screenshot alone does not verify interaction, semantics or data consistency.

### 6. Diagnose, repair and close coverage

Run `npm run build` and `npm run test:backend`, then the requirement-derived browser checks.
Build/backend success does not establish browser scenario coverage. Inspect actual errors and
exit statuses. Read the failing case's requirement and relevant browser/backend log, identify
its earliest broken prerequisite, make a focused repair and rerun it. Follow with affected
regressions; do not rewrite unrelated parts or weaken a check while behavior remains wrong.

Investigate environment problems using preflight information and actual module/browser launch
results. A missing global command does not prove an installed package is unavailable; resolve
the installed module using a compatible import/require. Reuse available browser binaries rather
than repeatedly reinstalling unchanged dependencies. Continue independent implementation/tests
while restoring a blocked check. Lower-level checks support diagnosis but do not certify a
browser scenario that never ran.

After each group, use the coverage map to choose the next missing functionality or failing
scenario. A partial summary, skipped check or environmental explanation does not complete the
task. Never invent passing evidence. Allocate the budget across implementation, integration,
testing and repair for the whole application. As it decreases, close gaps and failures rather
than starting large refactors or cosmetic polishing. Continue while execution remains available;
the runtime enforces hard limits.

### 7. Operate the workspace efficiently

Search relevant symbols and read bounded source ranges; reuse unchanged context. Batch
independent reads, but avoid concurrent edits to shared files or tests of partially written code.
Use manageable writes and inspect their results; huge multi-file commands may be truncated.
Use non-interactive commands, actual supported tool timeouts and the correct working directory.

For development servers, redirect logs, record PIDs and poll HTTP readiness with a bounded
deadline. On failure read the startup log. Stop only processes you started by their recorded
PIDs, avoiding broad `pkill -f` patterns. Keep test ports separate from final deployment and
release them when done. Retain application data, meaningful self-tests and their final results;
remove temporary probes and unrelated investigation debris.

## Command Execution Rules

You are operating in an environment where

1. You issue at least one command
2. The system executes the command(s) in a subshell
3. You see the result(s)
4. You write your next command(s)

Each response should include:

1. **Reasoning text** where you explain your analysis and plan
2. At least one tool call with your command

**CRITICAL REQUIREMENTS:**

- Your response SHOULD include reasoning text explaining what you're doing
- Your response MUST include AT LEAST ONE bash tool call. You can make MULTIPLE tool calls in a single response when the commands are independent (e.g., searching multiple files, reading different parts of the codebase).
- Directory or environment variable changes are not persistent. Every action is executed in a new subshell.
- However, you can prefix any action with `MY_ENV_VAR=MY_VALUE cd /path/to/working/dir && ...` or write/load environment variables from files

Example of a CORRECT response:
<example_response>
I need to understand the template structure first. Let me inspect the project layout and the task specification.

[Makes multiple bash tool calls: {"command": "ls -la"}, {"command": "cat package.json"}, {"command": "cat README.md | head -50"}]
</example_response>

## Environment Details

- You have a full Linux shell environment
- Always use non-interactive flags (-y, -f) for commands
- Avoid interactive tools like vi, nano, or any that require user input
- You can use bash commands or invoke any tool that is available in the environment
- You can also create new tools or scripts to help you with the task
- If a tool isn't available, you can also install it

## Submission

After the last application edit, rerun the build, backend checks and all scenario checks
needed to validate the final source. Review the coverage map: every required scenario must
have executed and passed; failures and not_run cases require further implementation/testing.
Rerun affected paths after any repair and preserve the actual results. Only then submit.
Do not replace these completion conditions with a claim that everything is verified.

When you've completed your work, you MUST finish with this EXACT command, standalone and not combined with any other command:

```bash
echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT
```

<CRITICAL>
After this command you cannot continue working (reading, editing, testing) on this task in any way.
</CRITICAL>
</instructions>"""


def build_task(checked: dict[str, Any], input_dir: Path) -> str:
    """Task-domain content only; the harness contract lives in UPSTREAM_INSTANCE_SKELETON."""
    lines = [
        "Implement and self-test the entire application using the workflow below.",
        "The original requirements and assets are staged under `.arc_requirements/`; preserve them unchanged.",
        "The YAML below is authoritative. Attached reference images guide visual implementation.",
        "",
        "FULL SOURCE requirements.yaml (verbatim; authoritative):",
        "```yaml",
        checked["raw_yaml"],
        "```",
        "",
        "REFERENCE ASSETS: .arc_requirements/reference/ contains the original files.",
        "The following reference images are attached to this message for visual interpretation:",
    ]
    attached_bytes = slimmed = 0
    for p in checked["images"]:
        lines.append(f"Image: {p.relative_to(input_dir).as_posix()}")
        payload, media, was_slimmed = _attach_image(p)
        attached_bytes += len(payload)
        slimmed += was_slimmed
        lines.append(_image_part(payload, media))
    emit(
        "images_attached",
        count=len(checked["images"]),
        original_bytes=sum(p.stat().st_size for p in checked["images"]),
        attached_bytes=attached_bytes,
        slimmed=slimmed,
    )
    return "\n".join(lines)


def _token_totals(records: list[dict]) -> dict[str, int | None]:
    """Aggregate per-attempt usage records; None when no attempt reported tokens."""
    usage_list = [record.get("usage") or {} for record in records]
    in_tokens = [
        u["prompt_tokens"]
        for u in usage_list
        if isinstance(u.get("prompt_tokens"), int)
    ]
    out_tokens = [
        u["completion_tokens"]
        for u in usage_list
        if isinstance(u.get("completion_tokens"), int)
    ]
    return {
        "input_tokens": sum(in_tokens) if in_tokens else None,
        "output_tokens": sum(out_tokens) if out_tokens else None,
    }


def _model_kwargs(request_timeout: float) -> dict[str, Any]:
    """Transport kwargs for litellm.completion; ARC_REASONING_EFFORT='' restores the
    endpoint default by omitting the parameter entirely."""
    kwargs: dict[str, Any] = {
        "api_base": os.environ["OPENAI_BASE_URL"],
        "timeout": request_timeout,
        "num_retries": 0,
    }
    effort = os.environ.get("ARC_REASONING_EFFORT", "low")
    if effort:
        kwargs["reasoning_effort"] = effort
    return kwargs


def _upstream_config(name: str) -> dict[str, Any]:
    """Load a shipped minisweagent config verbatim as the prompt/limit source of truth."""
    resource = importlib.resources.files("minisweagent.config").joinpath(name)
    return yaml.safe_load(resource.read_text(encoding="utf-8"))


def run_agent(
    checked: dict[str, Any],
    input_dir: Path,
    output_dir: Path,
    model_name: str,
    max_steps: int,
    max_seconds: int,
) -> dict[str, Any]:
    """Import upstream engine only when a real run is requested."""
    importing = time.monotonic()
    emit("engine_import_start")
    import litellm
    from minisweagent.agents.default import DefaultAgent
    from minisweagent.environments.local import LocalEnvironment
    from minisweagent.models.litellm_model import LitellmModel

    litellm.suppress_debug_info = True
    # Adopt the shipped tool-calling benchmark config (prompt/limits) and its shell env.
    upstream = _upstream_config("benchmarks/swebench.yaml")
    for name, value in (
        _upstream_config("default.yaml").get("environment", {}).get("env", {}).items()
    ):
        os.environ.setdefault(name, value)

    emit("engine_import_end", seconds=round(time.monotonic() - importing, 3))

    class LoggedModel(ModelProgress, LitellmModel):
        pass

    class LoggedEnvironment(BashProgress, LocalEnvironment):
        pass

    injected = variable_presence()
    emit(
        "environment_check",
        api_key_present=injected["OPENAI_API_KEY"],
        api_base_present=injected["OPENAI_BASE_URL"],
        model=model_name,
        arc_model_present=injected["ARC_MODEL"],
        platform_model_present=injected["MODEL"],
    )
    # Retry budget: failed attempts are typically unbilled (gateway errors return no usage)
    # and losing a run costs all accumulated progress — so outlive gateway degradation
    # episodes (t8 died after 2 attempts on a 180s gateway timeout). The platform runner's
    # own patience is the real ceiling; override via env.
    os.environ.setdefault("MSWEA_MODEL_RETRY_STOP_AFTER_ATTEMPT", "100")
    request_timeout = float(os.environ.get("ARC_REQUEST_TIMEOUT", "600"))
    if request_timeout <= 0:
        raise ValueError("ARC_REQUEST_TIMEOUT must be positive")
    emit(
        "model_init_start",
        timeout_seconds=request_timeout,
        max_attempts=os.environ["MSWEA_MODEL_RETRY_STOP_AFTER_ATTEMPT"],
        reasoning_effort=os.environ.get("ARC_REASONING_EFFORT", "low") or None,
    )
    details = output_dir / ".arc_adapter"
    details.mkdir(parents=True, exist_ok=True)
    model = LoggedModel(
        model_name="openai/" + model_name.removeprefix("openai/"),
        model_kwargs=_model_kwargs(request_timeout)
        | upstream["model"].get("model_kwargs", {}),
        cost_tracking="ignore_errors",  # unknown custom-model prices must not stop execution
        multimodal_regex=MULTIMODAL_REGEX,
        observation_template=upstream["model"]["observation_template"],
        format_error_template=upstream["model"]["format_error_template"],
    )
    model.calllog_dir = details  # per-attempt calls.jsonl + payload deltas
    agent = DefaultAgent(
        model,
        LoggedEnvironment(cwd=str(output_dir.resolve()), timeout=300),
        system_template=upstream["agent"]["system_template"],
        instance_template=UPSTREAM_INSTANCE_SKELETON,
        step_limit=max_steps,
        wall_time_limit_seconds=max_seconds,
        cost_limit=0,  # upstream default 3.0 would abort runs on endpoints with unknown pricing
        output_path=output_dir / ".arc_adapter" / "trajectory.json",
    )
    start = time.monotonic()
    error, error_chain = None, []
    try:
        emit("task_prepare_start", images=len(checked["images"]))
        task = build_task(checked, input_dir)
        emit("agent_loop_start", task_bytes=len(task.encode("utf-8")))
        result = agent.run(task)
        status = result.get("exit_status", "unknown")
    except Exception as exc:
        emit(
            "agent_error",
            exception=type(exc).__name__,
            seconds=round(time.monotonic() - start, 3),
        )
        status = type(exc).__name__
        error = f"{type(exc).__name__}: {redact(str(exc))}"
        error_chain = exception_chain(exc)
    emit("agent_end", status=status, seconds=round(time.monotonic() - start, 3))
    records = getattr(model, "_call_records", [])
    summary = {
        "status": status,
        "error": error,
        "error_chain": error_chain,
        "request_timeout_seconds": request_timeout,
        "run_seconds": round(time.monotonic() - start, 2),
        "llm_calls": agent.n_calls,
        "model_http_attempts": len(records),
        **_token_totals(records),
        # Model pricing estimates are not confirmed actual API charges.
        "actual_api_cost_usd": None,
        "minisweagent_reported_cost_usd": round(agent.cost, 6)
        if agent.cost > 0
        else None,
        "output_dir": str(output_dir.resolve()),
        "startup_command": "bash deploy.sh",
        "default_app_url": "http://127.0.0.1:3000",
    }
    (details / "run_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    # Keep downloads small: replace image data URLs in audit artifacts with verifiable
    # placeholders (ARC_LOG_IMAGES=1 keeps originals for image-specific debugging).
    if os.environ.get("ARC_LOG_IMAGES") != "1":
        trajectory_file = details / "trajectory.json"
        if trajectory_file.exists():
            trajectory_file.write_text(
                elide_images(trajectory_file.read_text(encoding="utf-8"))
            )
    return summary
