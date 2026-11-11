"""ARC-Bench file/CLI adapter for upstream mini-swe-agent v2.4.6.

Uses upstream DefaultAgent, LitellmModel and LocalEnvironment, with local task
guidance, progress logging and Bash command wrapping. Upstream handles timeouts,
process cleanup and the tool-calling contract.
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
    BashShell,
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

## Objective

Implement the entire application specified by the supplied requirements and visual references.
Completion requires working user journeys and successful self-tests on the final source.
Use the existing template, preserve working behavior, and work through actual bash tool calls.
Keep each response's reasoning brief and tied to the next implementation or verification action.

## Recommended Workflow

### 1. Read requirements and establish coverage

Read the YAML hierarchy and references. Child requirements inherit applicable parent constraints.
Retain original IDs and include every scenario, negative case and alternative. Explicit messages,
roles, names, defaults, identities and starting contexts are contracts. References guide appearance.
Choose simple, consistent behavior for unspecified details without adding unrelated scope.

Inspect package scripts, UI, routes, API and storage. Order work by dependencies: establish
navigation, identity and shared data flow, then implement related features in manageable groups.
Complete each group's UI, business rules and persistence together while covering the whole app.

Keep a compact local map using this format:
`scenario ID | test file/case | not_run/failed/passed | execution evidence or next repair`.
Use a requirement ID plus a short case name if scenario IDs are absent. Put GIVEN setup, WHEN
actions and THEN assertions in the tests; avoid duplicating them in a report. Update the map
after each feature group. A passed entry must reference an actual execution on the relevant
source; creating a test or repairing a shared component does not certify dependent scenarios.

### 2. Implement and verify each group

Implement each scenario's full path: specified page and identity -> visible entry -> interaction
-> observable result -> required persistence. Use the check standards below to write small,
requirement-derived tests as you implement. Reuse installed tooling, existing application tests
and small interaction helpers; retain meaningful self-tests for reruns.

During development, run focused checks and affected regressions. Check shared entry points early;
when authentication, navigation, forms or storage change, rerun their affected groups. Execute
downstream assertions after repairing a prerequisite. Inspect layout against reference images
alongside behavior. Reserve time for integration, testing and repair across the entire application.

### 3. Diagnose failures and choose the next action

Read the failing scenario's original requirement and actual error. Before editing a failing test,
determine whether the application violates the requirement or the test misrepresents it, and
briefly state the basis. Preserve the specified starting context, identity, action and outcome.
Repair the earliest broken prerequisite, rerun the case, then run affected regressions.

If a failure repeats, reassess fixture/session state, the running build/server, asynchronous
completion, locator scope and shared causes. Gather evidence that distinguishes these causes;
avoid repeatedly rerunning the same command or weakening assertions to obtain a pass.

For environment failures, inspect `.arc/preflight.json` if present and actual import/launch errors.
A missing global command does not prove the package is absent: try a compatible import/require
and available browser binaries before reinstalling. Continue independent implementation or
checks while restoring the environment. Lower-level checks do not certify an unexecuted browser
scenario. Never invent passing evidence or mark skipped cases passed.

Use the coverage map to choose the next missing feature or failed/not_run scenario. As budget
decreases, close functional gaps and failures before cosmetic polishing or large refactors.
Continue while execution is available; the runtime enforces hard limits.

## Check Standards

### Business state and persistence

- Supply required GIVEN records and relationships through normal, idempotent initialization or
  migrations. Preserve existing data and IDs; restarting must not reset edits. Create test data
  through user actions when those actions are part of the scenario.
- Keep writes, stored fields, reads and UI state consistent. Verify required reload/reopen,
  restart and account switching. Use the specified persistence mechanism; browser-only state
  cannot substitute for required shared or account-specific backend storage.
- Await the relevant write before announcing durable success and show real save errors. Guard
  initial loads, queued saves and delayed responses so stale results cannot overwrite newer
  edits, records or navigation. Initialization and live creation must obey the same invariants.
- Model required states and transitions explicitly, including draft/published, unpaid/paid,
  cancelled and archived/deleted. Confirm commits once; cancel/decline preserves prior state.
  Verify the final record and required backward/reopen behavior in multi-step journeys.
- Keep entity/variant, quantity, price, totals and availability consistent. Validate before
  side effects; rejected operations must not partially change records, stock or balances.
  Enforce ownership on backend reads/writes as well as UI controls. Check anonymous/second-user
  access where required. Apply these rules only to business behavior requested by the task.

### Browser entry and semantics

Start each scenario at its specified GIVEN page, identity and data; exercise actual navigation
and controls. Direct URLs, API calls or forced state can help diagnosis but cannot replace a
required entry or action. Identify records by their full business identity. Use independent
case setup and isolated sessions; use a disposable application/database copy for destructive
checks, preserving the working application's data.

Assert the property the requirement specifies: visible text, accessible name, description and
input value are distinct. Use semantic controls, associated labels and accurate selected,
checked, pressed, current, expanded and disabled states. Decorative icons, punctuation and
CSS-generated text must not alter a required accessible name. A visible notification does not
automatically have a status role or a name matching its text.

For specified roles/names use `getByRole(role, { name, exact: true })`, scoped to the relevant
record/container/dialog. Check visibility and uniqueness within that scope when one match is
required, then state and behavior. For a required status named "Saved", for example:

```javascript
const saved = page.getByRole('status', { name: 'Saved', exact: true });
await expect(saved).toHaveCount(1);
await expect(saved).toBeVisible();
```

Repeated controls are valid when their records distinguish them. Index selection is appropriate
when specified ordering or verified business identity justifies it; do not use `.first()` or
`.nth()` merely to bypass ambiguity. Include required filter combinations, validation messages,
confirmation/decline branches and persistence assertions, not just clicks or page advancement.

Use auto-retrying assertions and wait for specific states or acknowledged operations. Avoid
fixed sleeps and blanket networkidle waits that conceal unusable startup or incomplete saves.
For risky asynchronous paths, test interaction during loading and consecutive saves/navigation;
use controlled response delays when needed to expose stale updates. Such timing probes need
not be added to unrelated static flows. Fix operation ownership rather than extending timeouts.

### Executable assertions and trustworthy results

Use the installed assertion library or assertions that throw on mismatch. Every THEN outcome
needs an assertion. Screenshots, printed counts/PASS/FAIL and reaching the end of a script are
diagnostics; they cannot establish success. Build and backend checks support browser testing
but cannot replace scenario execution.

Unexpected statuses, browser exceptions and assertion mismatches must fail their relevant checks.
Assert the expected rejection and resulting unchanged state for negative cases. If collecting
failures, continue independent cases and finish with a nonzero exit if any failed. Catch blocks
must propagate failure or set `process.exitCode = 1`. Cases after an early abort remain not_run.
For a custom assertion harness, confirm a temporary failing probe exits nonzero, then remove it.

Run build, backend tests and browser checks through the supplied check runner, for example:
`python3 scripts/run_check.py --log /tmp/build.log -- npm run build` or
`python3 scripts/run_check.py --log /tmp/browser.log -- node tests/check.cjs`.
Issue each runner invocation as its own tool call, optionally preceded by `cd ... &&`;
do not append echo, log printing or `|| true`. The runner prints captured output and exits
with the check's status. Use separate calls for separate checks. Tool commands use Bash with
pipefail; this catches pipeline failures, but a later successful command can still mask an
earlier failure. A script that catches errors must itself return nonzero.

## Workspace and Tool Constraints

- Modify application source and add self-tests. Preserve `deploy.sh`, supplied tests/assertions
  and their harness, and `.arc_requirements/` unchanged. Correct your own tests only against
  the original requirements, following the failure diagnosis above.
- Use supplied requirements/assets, application source, dependencies and ordinary documentation.
  Do not seek external evaluator tests, platform submission internals, benchmark answers or
  other runs. Implement general behavior without scenario-title/account/fixture special cases.
- `.arc_adapter/` and `.arc/stdout.log` are audit artifacts, not task input. Preflight describes
  environment capabilities, not acceptance evidence.
- Search relevant symbols and bounded source ranges. Batch independent reads; keep dependent
  edits and checks sequential. Use manageable writes and inspect results. Reuse unchanged
  context and dependencies rather than repeatedly dumping files or reinstalling packages.
- Start servers with redirected logs, recorded PIDs and bounded HTTP readiness checks. Read
  startup logs on failure. Stop only your recorded processes; avoid broad `pkill -f`. Keep
  disposable test ports separate from final deployment and release them when finished.
- Retain application data, meaningful tests and final results. Remove temporary probes and
  unrelated investigation debris. Use non-interactive commands and supported tool timeouts.

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

On the final application source, run `npm run build`, `npm run test:backend` and all
requirement-derived scenario checks. Review actual exit statuses and the coverage map: every
required scenario must have executed and passed. Repair failures and execute not_run cases;
after any application edit, rerun affected checks and refresh the final full validation.
Preserve the results. Submit only when these conditions are met; a partial summary or a claim
of verification does not replace them.

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

    class LoggedEnvironment(BashProgress, BashShell, LocalEnvironment):
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
