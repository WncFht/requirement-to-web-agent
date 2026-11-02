"""Conservative pipeline receipts, separate from resumable stage-local checkpoints."""

from contextlib import contextmanager
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import sys

from dotenv import dotenv_values

from infrastructure.stages.requirements.tree import RequirementTree
from infrastructure.utils.files import save_json

STATE = ".arc/pipeline_state.json"
RESTART = "Use a new --output directory; existing artifacts were preserved."
IGNORED = {"__pycache__", "node_modules", ".git", ".venv", "dist"}


def digest(value):
    return sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def file_hashes(root: Path, paths) -> dict:
    result = {}
    for path in sorted(set(paths)):
        if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError(f"Unsafe pipeline input/output path: {path}")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = sha256(
                path.read_bytes()
            ).hexdigest()
    return result


def walk_files(root: Path):
    for directory, names, files in os.walk(root, followlinks=False):
        names[:] = sorted(name for name in names if name not in IGNORED)
        for name in names:
            if (Path(directory) / name).is_symlink():
                raise ValueError(
                    f"Symlink directory is not supported: {Path(directory) / name}"
                )
        for name in files:
            yield Path(directory) / name


def identity(source: Path, inputs: Path) -> dict:
    """Hash executable sources, input bytes and allowlisted effective configuration; never keys."""
    sources = [
        *(source / "legacy").glob("*.py"),
        source / "run_all.py",
        source / "main.py",
    ]
    sources.extend(
        p for p in walk_files(source / "infrastructure") if p.suffix != ".pyc"
    )
    sources.extend(
        source / name for name in ("pyproject.toml", "requirements.txt", "uv.lock")
    )
    # Discover literal flags from the compiler, avoiding arbitrary environment values.
    names = {
        "MODEL",
        "VISUAL_MODEL",
        "OPENAI_BASE_URL",
        "VISUAL_BASE_URL",
        "MAX_OUTPUT_TOKENS",
    }
    for path in sources:
        if path.suffix == ".py" and path.is_file():
            names.update(
                re.findall(
                    r"""os\.getenv\(\s*["'](ARC_[A-Z0-9_]+)["']""",
                    path.read_text(encoding="utf-8-sig"),
                )
            )
    names.discard("ARC_DISABLE_TIMING")
    effective = {**dotenv_values(source / ".env"), **os.environ}
    configuration = {name: effective.get(name) for name in sorted(names)}
    configuration["python"] = list(sys.version_info[:3])
    return {
        "input": digest(file_hashes(inputs, walk_files(inputs))),
        "compiler": digest(file_hashes(source, sources)),
        "configuration": digest(configuration),
    }


def workspace(output: Path) -> dict:
    """Seal compiler IR, application source, generated tests and build configuration, not runtime data."""
    paths = list((output / ".arc").glob("*.json"))
    paths = [p for p in paths if p.name != "pipeline_state.json"]
    for relative in (
        "backend/src",
        "backend/tests",
        "backend/scripts",
        "frontend/src",
        "frontend/tests",
        "frontend/public",
    ):
        paths.extend(
            p
            for p in walk_files(output / relative)
            if not (
                relative == "frontend/tests"
                and any(
                    part.startswith("fixed-")
                    for part in p.relative_to(output / relative).parts
                )
            )
        )
    for directory in (output, output / "backend", output / "frontend"):
        if directory.is_dir():
            paths.extend(
                p
                for p in directory.iterdir()
                if p.is_file()
                and p.suffix in {".json", ".ts", ".js", ".mjs", ".html"}
                and p.name
                not in {
                    "experiment.json",
                    "call-summary.json",
                    "timing-summary.json",
                    "vite.fixed.config.ts",
                    "playwright.fixed.config.ts",
                }
            )
    return file_hashes(output, paths)


def read(output, relative):
    value = json.loads((output / relative).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"Pipeline artifact must be a JSON object: {relative}")
    return value


def validate_completion(output: Path, step: str) -> None:
    """Check pass-boundary artifacts in addition to a successful child exit."""
    number = int(step[:2])
    required = {
        0: ("package.json",),
        1: (".arc/requirements.json", ".arc/visual_analysis.json"),
        2: (".arc/db_schema.json",),
        3: (".arc/db_obligations.json",),
        6: (".arc/backend_apis.json",),
        7: (".arc/backend_contracts.json",),
        9: (".arc/ui_design.json",),
        11: (".arc/ui_interactions.json",),
    }
    for relative in required.get(number, ()):
        if not (output / relative).is_file():
            raise ValueError(f"{step}: missing completion artifact {relative}")
        read(output, relative)
    if number == 2:
        leaves = RequirementTree(read(output, ".arc/requirements.json")).leaves
        if set(read(output, ".arc/db_schema.json")["requirements"]) != set(leaves):
            raise ValueError(f"{step}: schema does not cover every leaf requirement")
    if number == 5:
        entities = read(output, ".arc/db_schema.json")["entities"]
        required_sql = [f"backend/src/db/tables/{name}.sql" for name in entities]
        for relative in [*required_sql, "backend/src/db/initialize.ts"]:
            if not (output / relative).is_file():
                raise ValueError(f"{step}: missing completion artifact {relative}")
    reports = {8: "backend_tdd.json", 10: "ui_checks.json", 12: "frontend_e2e.json"}
    if number in reports:
        status = read(output, ".arc/" + reports[number]).get("status")
        if status == "GREEN":
            return
        empty_status = "NO_APIS" if number == 8 else "NO_UI"
        collection = read(
            output,
            ".arc/backend_contracts.json" if number == 8 else ".arc/ui_design.json",
        )
        key = "apis" if number == 8 else "pages"
        if status != empty_status or collection[key]:
            raise ValueError(
                f"{step}: completion requires GREEN or a verified empty design, got {status!r}"
            )


@contextmanager
def pipeline_lock(output: Path):
    path = output / ".arc/pipeline.lock"
    if path.parent.is_symlink():
        raise ValueError("Pipeline metadata directory cannot be a symlink")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise ValueError(
            "Pipeline lock exists. Check for a live writer; remove only a stale lock after it has stopped."
        ) from error
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(str(os.getpid()) + "\n")
        yield
    finally:
        path.unlink(missing_ok=True)


class PipelineState:
    """Reuse only a proven successful prefix under identical provenance and workspace bytes.

    Dependency invalidation is deliberately whole-run: changed inputs, code, config
    or edited artifacts require an isolated output, rather than reusing stale local
    checkpoints. Normal child failures retain their checkpoint but never a receipt.
    A hard-killed writer leaves active state and is not automatically trusted.
    """

    def __init__(self, source, inputs, output, steps, resume):
        self.output, self.steps = output, tuple(steps)
        self.identity_check = lambda: identity(source, inputs)
        self.expected = identity(source, inputs)
        path = output / STATE
        current = workspace(output)
        if path.exists():
            try:
                self.data = read(output, STATE)
                if self.data["version"] != 1 or self.data["steps"] != list(steps):
                    raise ValueError("state version or stage order changed")
                if not resume:
                    raise ValueError(
                        "managed output exists; use --resume for identical work"
                    )
                if self.data["identity"] != self.expected:
                    changed = [
                        k
                        for k in self.expected
                        if self.data["identity"].get(k) != self.expected[k]
                    ]
                    raise ValueError("provenance changed: " + ", ".join(changed))
                if self.data["active"] is not None:
                    raise ValueError(
                        "previous writer ended without sealing its checkpoint"
                    )
                if self.data["workspace"] != current:
                    raise ValueError(
                        "compiler artifacts or application files changed outside the pipeline"
                    )
                done = self.data["completed"]
                if not isinstance(done, list) or done != list(steps[: len(done)]):
                    raise ValueError("completion records are not a valid stage prefix")
                for step in done:
                    validate_completion(output, step)
            except (OSError, ValueError, KeyError, TypeError) as error:
                raise ValueError(
                    f"Cannot reuse pipeline output: {error}. {RESTART}"
                ) from error
        else:
            if current:
                raise ValueError(
                    f"Existing output has no trusted pipeline completion records. {RESTART}"
                )
            self.data = {
                "version": 1,
                "steps": list(steps),
                "identity": self.expected,
                "completed": [],
                "active": None,
                "workspace": current,
            }
            self.publish()

    def publish(self):
        save_json(self.output / STATE, self.data)

    def completed(self, step):
        return step in self.data["completed"]

    def begin(self, step):
        if step != self.steps[len(self.data["completed"])]:
            raise ValueError("Pipeline must run the first incomplete stage")
        self.data["active"] = step
        self.publish()

    def finish(self, step, success):
        # A normal interrupt stops the child before sealing partial work. SIGKILL
        # cannot do this and deliberately leaves active state for a fail-closed restart.
        if self.identity_check() != self.expected:
            raise ValueError(
                f"Compiler/input/configuration changed during execution. {RESTART}"
            )
        try:
            if success:
                validate_completion(self.output, step)
                self.data["completed"].append(step)
        finally:
            self.data["workspace"] = workspace(self.output)
            self.data["active"] = None
            self.publish()
