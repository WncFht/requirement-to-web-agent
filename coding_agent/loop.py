"""A single read/edit/check loop, with coarse test freezing and global budgets."""

import json
from pathlib import Path
import subprocess
import sys
from time import monotonic

import yaml

from coding_agent.checks import Checks, prepare_project
from coding_agent.model import Model
from coding_agent.protocol import BudgetExhausted, InvalidTest, green, observation
from coding_agent.trace import Trace, file_manifest, fingerprint, json_write
from coding_agent.workspace import Workspace, TEST_FILES


def compact(value, limit=12000):
    """Keep structured failures and explicit omission counts; raw artifacts retain everything."""
    if isinstance(value, str):
        return (
            value
            if len(value) <= limit
            else value[:limit]
            + f"\n[omitted {len(value) - limit} characters; full data in trace]"
        )
    if isinstance(value, list):
        return [compact(x, limit) for x in value[:12]] + (
            [{"omitted_items": len(value) - 12}] if len(value) > 12 else []
        )
    if isinstance(value, dict):
        return {
            k: compact(v, limit)
            for k, v in value.items()
            if k not in {"stdout", "raw_report"}
        }
    return value


def requirements(inputs):
    root = Path(inputs)
    text = (root / "requirements.yaml").read_text(encoding="utf-8-sig")
    parsed = yaml.safe_load(text)
    if not isinstance(parsed, dict):
        raise ValueError("Requirement root must be a mapping")
    supplied = {"requirements.yaml": text}
    for path in sorted((root / "tests").rglob("*.ts")):
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError("Unsafe supplied reference test")
        supplied[path.relative_to(root).as_posix()] = path.read_text(
            encoding="utf-8-sig"
        )
    images = []

    def visit(value):
        if isinstance(value, dict):
            ref = value.get("reference")
            if isinstance(ref, str) and not ref.startswith("\\ref"):
                path = root / ref
                if not path.resolve().is_relative_to(root) or path.is_symlink():
                    raise ValueError("Unsafe image path")
                if path.is_file():
                    images.append("input/" + ref)
            for item in value.values():
                visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(parsed)
    return supplied, sorted(set(images))


def progress_key(output, phase, action, response):
    """Timing/log noise cannot make an unchanged repeated check count as progress."""
    checks = response.get("checks", {})
    if "name" in checks:
        checks = {checks["name"]: checks}
    outcomes = {
        name: {k: row.get(k) for k in ("status", "passed", "failed", "returncode")}
        for name, row in checks.items()
    }
    return (
        fingerprint(file_manifest(output)),
        phase,
        json.dumps(action, sort_keys=True),
        response["status"],
        response["summary"],
        json.dumps(outcomes, sort_keys=True),
    )


class Agent:
    def __init__(self, config, model_factory=Model, checks_factory=Checks):
        self.config = config
        self.trace = Trace(config.output)
        self.workspace = Workspace(config.output, config.inputs, self.trace)
        self.model = model_factory(config, self.trace)
        self.checks = checks_factory(config.output, self.trace, self.remaining)
        self.history = []
        self.phase = "PREPARE_TESTS"
        self.repeat = 0
        self.last_progress = None
        self.turn = 0

    def remaining(self):
        return self.config.max_seconds - (monotonic() - self.trace.started)

    def context(self, supplied, images):
        contract = self.config.output / "APP_CONTRACT.md"
        payload = {
            "phase": self.phase,
            "turn": self.turn,
            "remaining_seconds": round(self.remaining()),
            "remaining_tokens": self.config.max_tokens - self.trace.tokens,
            "inputs": supplied,
            "contract": contract.read_text() if contract.exists() else None,
            "files": self.workspace.inventory(),
            "required_test_paths": sorted(TEST_FILES),
        }
        seed = {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}
        history = self.history
        if len(json.dumps(history, ensure_ascii=False)) > 100000:
            removed = len(history) - 10
            history = self.history[-10:]
            self.history = history
            self.trace.emit(
                "context.compact",
                removed_messages=removed,
                retained_messages=len(history),
            )
        messages = [
            {
                "role": "system",
                "content": Path(__file__)
                .with_name("prompts")
                .joinpath("system.txt")
                .read_text(),
            },
            seed,
            *history,
        ]
        if self.turn == 1 and images:
            parts = [
                {
                    "type": "text",
                    "text": "Reference images in order: " + ", ".join(images),
                }
            ]
            parts.extend(item["image"] for item in self.workspace.read(images))
            messages.append({"role": "user", "content": parts})
        return messages

    def execute(self, action):
        if action.get("invalid_test"):
            raise InvalidTest(str(action["invalid_test"]))
        kind = action["action"]
        if kind == "read":
            items = self.workspace.read(
                action["paths"], action.get("start", 1), action.get("limit", 180)
            )
            images = [x.pop("image") for x in items if "image" in x]
            return observation("OK", "Files read", files=items), images
        if kind == "search":
            return observation(
                "OK", "Search results", **self.workspace.search(action["query"])
            ), []
        if kind == "edit":
            changes = self.workspace.apply(action["edits"])
            return observation(
                "OK",
                "Edits applied; existing failed checks are not automatically GREEN",
                edits=changes,
            ), []
        if kind == "check":
            return observation(
                "OK", "Actual check results", checks=self.checks.run(action["name"])
            ), []
        if self.phase == "PREPARE_TESTS":
            hashes = self.checks.freeze()
            self.workspace.frozen = True
            self.phase = "IMPLEMENT"
            return observation(
                "OK",
                "Tests frozen. Implement the whole application now; tests/support cannot change.",
                frozen=hashes,
            ), []
        results = self.checks.run("all")
        if not all(green(row) for row in results.values()):
            return observation(
                "FAILED", "Final checks failed; repair application code", checks=results
            ), []
        return observation(
            "INTERNAL_GREEN",
            "Every internal check and production build passed",
            checks=results,
        ), []

    def run(self):
        supplied, images = requirements(self.config.inputs)

        def leaves(node):
            return (
                [
                    identity
                    for child in node.get("children", [])
                    for identity in leaves(child)
                ]
                if node.get("children")
                else [node["id"]]
            )

        self.checks.required_ids = leaves(yaml.safe_load(supplied["requirements.yaml"]))
        compiler = Path(__file__).resolve().parents[1]
        compiler_files = {}
        from coding_agent.trace import sha

        for directory in (compiler / "coding_agent", compiler / "infrastructure"):
            for path in sorted(directory.rglob("*")):
                if (
                    path.is_file()
                    and path.suffix != ".pyc"
                    and "__pycache__" not in path.parts
                ):
                    compiler_files[path.relative_to(compiler).as_posix()] = sha(path)
        for name in ("main.py", "requirements.txt"):
            compiler_files[name] = sha(compiler / name)
        json_write(
            self.trace.root / "run.json",
            {
                "version": 1,
                "run_id": self.trace.run_id,
                "configuration": self.config.public(),
                "inputs": file_manifest(self.config.inputs),
                "compiler_files": compiler_files,
                "compiler_sha256": fingerprint(compiler_files),
                "python": list(sys.version_info[:3]),
                "model_adapter": type(self.model).__name__,
            },
        )
        self.trace.emit("run.start", configuration=self.config.public())
        status, error = "BUDGET_EXHAUSTED", None
        try:
            self.checks.install()
            self.trace.emit(
                "environment.ready",
                node=self.checks.execute(["--version"])["stdout"].strip(),
                dependency_lock_sha256=sha(self.config.output / "package-lock.json"),
            )
            for self.turn in range(1, self.config.max_turns + 1):
                if (
                    self.remaining() <= 0
                    or self.trace.tokens + self.config.output_tokens
                    > self.config.max_tokens
                ):
                    raise BudgetExhausted("Shared run budget exhausted")
                print(
                    f"Coding agent | {self.phase} | turn {self.turn}/{self.config.max_turns} | tokens {self.trace.tokens}",
                    flush=True,
                )
                action = None
                try:
                    self.trace.emit("turn.start", turn=self.turn, phase=self.phase)
                    action, raw = self.model.generate(
                        self.context(supplied, images), self.remaining()
                    )
                    self.trace.emit(
                        "action.start", turn=self.turn, action=action["action"]
                    )
                    response, image_parts = self.execute(action)
                    self.history.append({"role": "assistant", "content": raw})
                except InvalidTest as exc:
                    if self.phase == "IMPLEMENT":
                        raise
                    response, image_parts = (
                        observation(
                            "ERROR", "Repair tests BEFORE freezing: " + str(exc)
                        ),
                        [],
                    )
                except (ValueError, OSError, subprocess.SubprocessError) as exc:
                    response, image_parts = observation("ERROR", str(exc)), []
                reference = self.trace.artifact("observation", response)
                self.trace.emit(
                    "action.end",
                    turn=self.turn,
                    action=(action or {}).get("action"),
                    status=response["status"],
                    artifact=reference,
                )
                content = json.dumps(compact(response), ensure_ascii=False)
                if image_parts:
                    self.history.append(
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": content},
                                *image_parts,
                            ],
                        }
                    )
                else:
                    self.history.append({"role": "user", "content": content})
                print(
                    f"  {response['status']}: {response['summary'][:180]}", flush=True
                )
                if response["status"] == "INTERNAL_GREEN":
                    status = "INTERNAL_GREEN"
                    break
                signature = progress_key(
                    self.config.output, self.phase, action, response
                )
                self.repeat = self.repeat + 1 if signature == self.last_progress else 1
                self.last_progress = signature
                if self.repeat >= 3:
                    status = "NO_PROGRESS"
                    break
        except BudgetExhausted as exc:
            status, error = "BUDGET_EXHAUSTED", str(exc)
        except InvalidTest as exc:
            status, error = "INVALID_TEST", str(exc)
        except KeyboardInterrupt:
            status, error = "INTERRUPTED", "Interrupted by owner"
        except Exception as exc:
            status, error = (
                "TRANSPORT_FAILED"
                if "TRANSPORT_FAILED" in str(exc)
                else "FAILED_CHECK",
                str(exc).replace(self.config.api_key, "[redacted]"),
            )
        return self.trace.seal(
            status,
            phase=self.phase,
            turns=self.turn,
            error=error,
            checks=compact(self.checks.reports),
            frozen_tests=self.checks.frozen,
        )


def run(config, **factories):
    output = config.output
    if output.exists() and any(
        path.name != "node_modules" for path in output.iterdir()
    ):
        raise ValueError(
            "Use a fresh output directory; existing artifacts are preserved"
        )
    prepare_project(output, config.port)
    return Agent(config, **factories).run()
