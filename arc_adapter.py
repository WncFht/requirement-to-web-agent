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

You're a software engineer interacting continuously with a computer by submitting commands.
You'll be helping implement a complete web application that satisfies the task specification.
Your task is specifically to implement the required application in the current directory so that it behaves exactly as specified, in a way that is general and consistent with the provided template.
<IMPORTANT>This is an interactive process where you will think and issue AT LEAST ONE command, see the result, then think and issue your next command(s).</important>

For each response:

1. Include a THOUGHT section explaining your reasoning and what you're trying to accomplish
2. Provide one or more bash tool calls to execute

## Important Boundaries

- MODIFY: application source files in the current directory (this is the working directory for all your subsequent commands)
- DO NOT MODIFY: `deploy.sh`, supplied tests/assertions or their harness, or anything under `.arc_requirements/`
- Use application source, supplied public requirements/assets and ordinary dependency documentation.
  Do not search for or read external evaluator tests, platform submission internals, or hidden
  benchmark answers. Existing tests inside this application are available for verification.

## Recommended Workflow

### Read requirements as a contract

- Read the supplied YAML hierarchy and reference images. Preserve requirement IDs and
  applicable parent constraints when interpreting child features. Cover every scenario,
  including alternatives, validation, permissions, empty states and persistence.
- Treat specified starting pages, identities, labels, messages, defaults and accessible
  roles/names as observable behavior. Use screenshots for visual guidance alongside the
  written behavior. If a detail is unspecified, choose a simple implementation consistent
  with the application; do not replace explicit requirements with familiar product habits.
- Make a compact working checklist by requirement ID: implementation, actual check and
  next action needed to complete and verify it. Keep it in brief reasoning or a small local note; do not produce a long
  requirements report or repeatedly copy the YAML. A checklist is not proof of acceptance.

### Inspect, then implement complete paths

- Inspect package scripts, relevant routes, components, API handlers and storage before
  editing. Preserve working application code and use the template's existing stack.
- Order work by actual dependencies and shared implementation resources. Establish the
  essential navigation, identity and data flow first, then complete related features in
  bounded groups. Track independent features too, so early polishing does not consume
  all opportunities to implement later requirements. Do not redesign the whole project.
- For each feature, implement the full path: specified starting page and identity ->
  visible entry -> interaction -> correct result -> reload/reopen persistence where required.
  A schema, endpoint, static page, placeholder or success toast alone is not completion.
- Complete relevant UI, business logic and storage together before expanding the next
  group. Reuse shared validation/state paths; enforce required permissions on backend
  reads and writes as well as the UI. Do not hardcode scenario answers or special cases
  keyed to known fixture values.
- Provide the records and relationships explicitly assumed by GIVEN conditions through
  normal initialization or migration code. Initialization must be idempotent and must
  not overwrite user changes on restart. Preserve existing records and stable IDs;
  never reset a working database just to obtain a passing demonstration.

### Keep reads, writes and visible state consistent

- Compare frontend field names and object IDs with actual write requests, server storage
  and GET responses. Verify that reloading reconstructs the same state; an optimistic
  UI update cannot compensate for a missing write or incompatible response shape.
- Await the relevant write before claiming durable success. Display failed saves honestly.
  Prevent older asynchronous responses or queued writes from overwriting newer edits or
  navigating away from the user's current context. Keep related state changes consistent.
- Use the persistence mechanism required by the task. For persisted features, exercise
  refresh/reopen and a subsequent ordinary edit; when restart persistence is required,
  also restart the application. Do not substitute browser-only state for required shared
  or account-specific backend data.
- Give controls the specified visible labels and accessible semantics. Associate form
  labels with inputs, use buttons/links for their intended actions, and expose selection,
  errors and disabled states correctly. Required messages must be visible in the app;
  native browser validation alone does not implement a specified application error flow.

### Verify behavior with evidence

- Run the supplied build (`npm run build`) and backend checks (`npm run test:backend`).
  These establish build/API health, not coverage of all application requirements.
- Inspect `.arc/preflight.json` once if present for available browser/Playwright details.
  Use the installed browser tooling to exercise real user paths. Check the actual module
  and browser launch before declaring the browser unavailable; do not assume a missing
  global executable means an installed package is unusable.
- Verify scenarios from their specified GIVEN page, identity and data. Click the real
  entry and controls, perform WHEN, and inspect THEN, including required failures and
  state after reload. Direct URLs, API calls or hand-edited database values may help
  diagnose a failure but do not verify a missing UI entry or user interaction.
- Add focused self-checks when useful, using the public requirements as their source.
  Include negative cases and cross-feature paths, not just existence or happy-path checks.
  Own checks are proxies: if they disagree with the requirement, fix the implementation
  or correct the mistaken proxy; never weaken an assertion while its requirement is unmet.
- After a shared navigation, authentication or storage change, recheck affected working
  paths. Review every requirement ID and exercise every specified scenario, including
  previously unchecked paths. Verify visual structure against the reference images too.
- Use the checklist to drive implementation -> test -> diagnose -> fix -> retest until
  every requirement is implemented and its scenarios pass. Treat failed, skipped and
  unverified checks as open work, not as a reason to finish with a partial delivery.
- Record what actually ran and what it showed; never describe an unexecuted or skipped
  check as passing. Investigate environment failures and use available tooling or a
  compatible setup to restore verification. Lower-level checks can diagnose a blocker
  but do not replace required browser checks. Continue independent implementation and
  verification while resolving a blocker; do not stop at documenting it.

### Use tools and the remaining budget deliberately

- Search for relevant symbols, then read bounded source ranges. Reuse unchanged content
  already in context instead of dumping all specifications or rereading whole files.
  Batch independent reads; finish a manageable edit and inspect its result before expanding.
- Commands run in fresh subshells; include the working directory and needed environment
  each time. For pipelines used as checks, explicitly use `bash -o pipefail -c '...'`
  or otherwise preserve and inspect the actual failing command's exit status. Output
  from `tee`, `tail` or a final successful command is not evidence the check passed.
- Use non-interactive commands and timeouts supported by the actual tool. Split long
  setup/build/check work into bounded commands and inspect exit status and relevant logs.
  Do not repeatedly reinstall unchanged dependencies or rerun an unchanged failure.
- Start development servers with redirected logs and a recorded PID, poll readiness with
  a bounded deadline, then inspect the log if startup fails. A fixed sleep alone is not
  readiness evidence. Stop only processes you started by their recorded PIDs; avoid broad
  `pkill -f` patterns. Keep development-server ports separate from final deployment.
- Diagnose the concrete failing path and backend/browser error before broad rewrites.
  Fix a shared blocker once, then recheck dependent paths; do not keep polishing a single
  feature while unrelated required functionality remains absent.
- Allocate steps/time to completing the entire application, integration tests and repairs.
  As the budget decreases, prioritize closing missing functionality and failing scenarios;
  avoid large refactors and cosmetic polishing that delay completion. A partial-work
  summary does not satisfy the task. Keep implementing, testing and fixing while execution
  remains available; the runtime enforces hard limits.
- After the last source edit, run the final build, backend checks and scenario regression.
  Resolve failures and repeat affected checks before submission.

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

Submit only after all requirements are implemented, all specified scenarios have been
exercised successfully, and the final build and backend checks pass on the final source.
Review the requirement checklist for missing, failed or unverified paths and resolve them
before issuing the completion command. Reporting unfinished work or an environment blocker
does not satisfy these completion conditions. Never fabricate passing evidence.

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
        "Implement the complete web application specified in the supplied requirements.yaml.",
        "Implement the requirements as a general application, including persistence and all specified UI behavior.",
        "Preserve exact requirement behavior, accessibility names/roles, scenarios and test constraints.",
        "Use the reference screenshots to implement the visual design. Do not hardcode a benchmark answer or change tests.",
        "Do not read `.arc_adapter/` or `.arc/stdout.log` — audit logs for humans, not task input.",
        "Servers: use redirected logs and recorded PIDs, poll HTTP readiness with a bounded deadline, and stop only your own processes. Inspect startup logs instead of assuming a fixed sleep proves readiness.",
        "If available, `.arc/preflight.json` records the runner's preinstalled browser and Playwright version; it is environment information, not acceptance evidence.",
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
