"""Fixed commands and real application checks, independent of legacy design IR."""

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from time import monotonic
from uuid import uuid4

from coding_agent.protocol import BudgetExhausted, InvalidTest, green
from coding_agent.trace import file_manifest, fingerprint, json_write, sha
from coding_agent.workspace import TEST_FILES
from infrastructure.shared.project.initialize import initialize_project
from infrastructure.stages.backend.testing import BackendChecks
from infrastructure.stages.frontend.ui.runtime import (
    configure_tailwind,
    PLAYWRIGHT_VERSION,
)
from infrastructure.stages.frontend.ui.testing import (
    FrontendChecks,
    parse_playwright_result,
)
from infrastructure.stages.frontend.interactions.e2e_runtime import (
    prepare_e2e,
    CONFIG_SOURCE,
    RUNNER_SOURCE,
)
from infrastructure.utils.processes import stop_process, process_options, npm_command

HTTP_FIXTURE = """// Program-owned real HTTP/SQLite fixture. No application behavior is mocked.
import type { TestContext } from "node:test";
import { once } from "node:events";
import { createApp } from "../../src/app.js";
import { createTestDatabase } from "./context.js";
export async function appFixture(context: TestContext) {
  const database = createTestDatabase(context);
  const server = createApp(database).listen(0, "127.0.0.1");
  await once(server, "listening");
  context.after(async () => { await new Promise<void>(resolve => {
    server.close(() => resolve()); server.closeAllConnections();
  }); });
  const address = server.address();
  if (!address || typeof address === "string") throw new Error("No test server address");
  const base = `http://127.0.0.1:${address.port}`;
  async function send(method: string, path: string, body?: unknown, cookie?: string) {
    const headers: Record<string,string> = {};
    if (body !== undefined) headers["content-type"] = "application/json";
    if (cookie !== undefined) headers.cookie = cookie;
    const response = await fetch(base + path, {method,headers,
      ...(body === undefined ? {} : {body: JSON.stringify(body)})});
    const text = await response.text();
    return {status: response.status, body: (text ? JSON.parse(text) : null) as any,
      headers: response.headers, cookies: response.headers.getSetCookie()};
  }
  return {database, send};
}
"""


def application_environment(extra=None):
    return {
        k: v
        for k, v in {**os.environ, **(extra or {})}.items()
        if not k.startswith(("OPENAI_", "VISUAL_", "ARC_AGENT_"))
        and k not in {"MODEL", "DATABASE_URL"}
    } | (
        {"DATABASE_URL": extra["DATABASE_URL"]}
        if extra and "DATABASE_URL" in extra
        else {}
    )


def prepare_project(output, port=3000):
    output = Path(output)
    initialize_project(output)
    configure_tailwind(output)
    prepare_e2e(output, {})
    package = json.loads((output / "package.json").read_text())
    package.setdefault("devDependencies", {})["@playwright/test"] = PLAYWRIGHT_VERSION
    json_write(output / "package.json", package)
    config = CONFIG_SOURCE.replace(
        'testDir: "./tests/e2e"', 'testDir: "./tests"'
    ).replace("use: { baseURL:", "use: { actionTimeout: 5000, baseURL:")
    (output / "frontend/playwright.agent.config.ts").write_text(config)
    (output / "frontend/scripts/test-agent.mjs").write_text(
        RUNNER_SOURCE.replace(
            "frontend/playwright.e2e.config.ts", "frontend/playwright.agent.config.ts"
        )
    )
    frontend = json.loads((output / "frontend/tsconfig.json").read_text())
    frontend["compilerOptions"]["types"] = ["vite/client", "node"]
    frontend["include"] = ["src", "tests"]
    json_write(output / "frontend/tsconfig.json", frontend)
    (output / "backend/tests/support/http.ts").write_text(HTTP_FIXTURE)
    (output / "deploy.sh").write_text(
        '#!/usr/bin/env bash\nset -euo pipefail\ncd -- "$(dirname -- "${BASH_SOURCE[0]}")"\n'
        "npm install --include=dev --no-audit --no-fund\nnpm run db:init\nnpm run build\n"
        f'export PORT="${{PORT:-{port}}}"\nexport HOST="${{HOST:-0.0.0.0}}"\nexec npm start\n'
    )
    (output / "deploy.sh").chmod(0o755)


def validate_tests(output):
    """Reject known concrete setup contradictions and test bypasses before freezing."""
    output = Path(output)
    for name in sorted(TEST_FILES):
        path = output / name
        if not path.is_file():
            raise ValueError(f"Create required test suite: {name}")
        source = path.read_text()
        if re.search(
            r"\b(?:test|describe)\s*\.\s*(?:skip|only|todo|fixme|fail)\b|__ARC_UI_FIXTURE__|process\.exit|node:(?:fs|child_process)|\b(?:vi|jest)\.mock",
            source,
        ):
            raise InvalidTest(f"Forbidden test bypass/infrastructure access: {name}")
        if not re.search(r"\btest\s*\(", source):
            raise InvalidTest(f"No executable tests in {name}")
        if name.startswith("frontend/"):
            if re.search(
                r"page\.(?:request|route|addInitScript)|waitForTimeout\s*\(", source
            ):
                raise InvalidTest(
                    "Generated browser tests must exercise the real UI without mocks/injected state"
                )
            chunks = re.split(r"\btest\s*\(", source)[1:]
            for chunk in chunks:
                title = chunk.split("async", 1)[0]
                if re.search(
                    r"existing session|valid session|seeded session|signed in",
                    title,
                    re.I,
                ) and re.search(
                    r"seed\w*Session\s*\(|INSERT\s+INTO\s+[\"`]?Session", chunk, re.I
                ):
                    if "addCookies" not in chunk and not re.search(
                        r"\.(?:click|fill)\s*\(", chunk
                    ):
                        raise InvalidTest(
                            "A seeded database session needs its browser credential before asserting signed-in UI"
                        )
                selections = re.findall(r"\b(male|female)\.check\s*\(", chunk, re.I)
                asserted = re.findall(
                    r"(?:gender\??\.?|gender\])[^\n]{0,80}?toBe\s*\(\s*[\"'](Male|Female)[\"']",
                    chunk,
                )
                if (
                    selections
                    and asserted
                    and selections[-1].lower() != asserted[-1].lower()
                ):
                    raise InvalidTest(
                        "Last gender selection contradicts persisted gender assertion"
                    )


class Checks(FrontendChecks):
    def __init__(self, output, trace=None, remaining=None):
        super().__init__(Path(output), timeout=300)
        self.trace, self.remaining = trace, remaining or (lambda: 1200)
        self.reports = {}
        self.frozen = None
        self.required_ids = []

    def execute(self, args, *, env=None, timeout=None, executable=None):
        allowance = min(timeout or self.timeout, self.remaining())
        if allowance < 1:
            raise BudgetExhausted("No remaining check time")
        started = monotonic()
        process_id = uuid4().hex
        if self.trace:
            self.trace.emit(
                "process.start",
                process_id=process_id,
                command=[executable or self.node, *args],
            )
        process = subprocess.Popen(
            [executable or self.node, *args],
            cwd=self.output,
            env=application_environment(env),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            **process_options(),
        )
        try:
            stdout, stderr = process.communicate(timeout=allowance)
        except BaseException as error:
            stop_process(process)
            if self.trace:
                self.trace.emit(
                    "process.end",
                    process_id=process_id,
                    status=type(error).__name__,
                    seconds=monotonic() - started,
                )
            raise
        if self.trace:
            self.trace.emit(
                "process.end",
                process_id=process_id,
                returncode=process.returncode,
                seconds=monotonic() - started,
            )
        return {
            "returncode": process.returncode,
            "stdout": stdout,
            "output": (stdout + stderr)[-24000:],
        }

    def install(self):
        npm = shutil.which("npm")
        result = self.execute(
            ["install", "--include=dev", "--no-audit", "--no-fund"],
            executable=npm,
            timeout=600,
        )
        if result["returncode"]:
            raise ValueError("Dependency installation failed: " + result["output"])
        browser = self.execute(
            ["node_modules/@playwright/test/cli.js", "install", "chromium"], timeout=600
        )
        if browser["returncode"]:
            raise ValueError("Chromium installation failed: " + browser["output"])

    def test_hashes(self):
        return {p: sha(self.output / p) for p in sorted(TEST_FILES)}

    def ensure_frozen(self):
        if self.frozen is not None and self.frozen != self.test_hashes():
            raise InvalidTest("Frozen test bytes changed")

    def _typecheck(self):
        back = BackendChecks.typecheck(self)
        front = self.execute(
            [
                "node_modules/typescript/bin/tsc",
                "--noEmit",
                "-p",
                "frontend/tsconfig.json",
            ]
        )
        return {
            "returncode": back["returncode"] or front["returncode"],
            "passed": int(back["returncode"] == 0 and front["returncode"] == 0),
            "failed": int(back["returncode"] != 0 or front["returncode"] != 0),
            "output": back["output"] + "\n" + front["output"],
        }

    def _backend(self):
        result = self.execute(
            [
                "--import",
                "tsx",
                "--test",
                "--test-reporter=tap",
                "backend/tests/contract.test.ts",
            ]
        )
        for key, field in (
            ("tests", "tests"),
            ("pass", "passed"),
            ("fail", "failed"),
            ("skipped", "skipped"),
            ("todo", "todo"),
        ):
            found = re.search(rf"^# {key} (\d+)\s*$", result["stdout"], re.M)
            result[field] = int(found.group(1)) if found else 0
        if not result["tests"]:
            result["errors"] = ["Backend runner produced no test cases"]
        return result

    def _browser(self, name):
        relative = (
            "frontend/tests/ui/presence.spec.ts"
            if name == "ui"
            else "frontend/tests/e2e/workflows.spec.ts"
        )
        result = self.execute(
            ["frontend/scripts/test-agent.mjs", relative], timeout=300
        )
        raw = json.loads(result["stdout"])
        expected_failures = 0

        def visit(suite):
            nonlocal expected_failures
            for spec in suite.get("specs", []):
                for test in spec.get("tests", []):
                    expected_failures += (
                        test.get("expectedStatus", "passed") != "passed"
                    )
            for child in suite.get("suites", []):
                visit(child)

        visit(raw)
        result = parse_playwright_result(result, include_files=True)
        result["expected_failures"] = expected_failures
        result["raw_report"] = raw
        diagnostics = self.output / "frontend/test-results/e2e"
        if self.trace and diagnostics.exists():
            saved = self.trace.root / "artifacts" / ("browser-" + uuid4().hex)
            shutil.copytree(diagnostics, saved, symlinks=True)
            result["browser_evidence"] = {
                "path": saved.relative_to(self.output).as_posix(),
                "files": file_manifest(saved, logs=True),
            }
        return result

    def run(self, name):
        if name not in {"typecheck", "backend", "ui", "e2e", "build", "all"}:
            raise ValueError("Unknown check name")
        self.ensure_frozen()
        if name == "all":
            return {
                k: self.run(k) for k in ("typecheck", "backend", "ui", "e2e", "build")
            }
        check_id, started = uuid4().hex, monotonic()
        files = file_manifest(self.output)
        version = fingerprint(files)
        if self.trace:
            self.trace.emit(
                "check.start", check_id=check_id, name=name, application_sha256=version
            )
        try:
            if name == "typecheck":
                result = self._typecheck()
            elif name == "backend":
                result = self._backend()
            elif name in {"ui", "e2e"}:
                result = self._browser(name)
            else:
                command = npm_command()
                result = self.execute(
                    [*command[1:], "run", "build"], executable=command[0]
                )
                result.update(
                    passed=int(result["returncode"] == 0),
                    failed=int(result["returncode"] != 0),
                )
        except (ValueError, subprocess.SubprocessError, BudgetExhausted) as error:
            result = {
                "returncode": 1,
                "passed": 0,
                "failed": 1,
                "errors": [type(error).__name__],
                "output": str(error)[-12000:],
            }
        self.ensure_frozen()
        result.update(
            name=name,
            application_sha256=version,
            seconds=monotonic() - started,
            status="GREEN" if green(result) else "FAILED",
        )
        self.reports[name] = result
        if self.trace:
            self.trace.emit(
                "check.end",
                check_id=check_id,
                name=name,
                status=result["status"],
                seconds=result["seconds"],
                artifact=self.trace.artifact("check", result),
            )
        return result

    def freeze(self):
        validate_tests(self.output)
        test_source = "\n".join((self.output / name).read_text() for name in TEST_FILES)
        missing = [
            identity for identity in self.required_ids if identity not in test_source
        ]
        if missing:
            raise ValueError(
                "Generated tests omit requirement identifiers: " + ", ".join(missing)
            )
        compiled = self.run("typecheck")
        if not green(compiled):
            raise ValueError(
                "Test compilation must pass before freezing: " + compiled["output"]
            )
        for name in ("backend", "ui", "e2e"):
            report = self.run(name)
            if green(report):
                raise ValueError(
                    f"{name} tests already pass on the empty application; require meaningful behavioral RED"
                )
            diagnostic = report.get("output", "")
            failures = report.get("failures", [])
            if (
                report.get("errors")
                or report.get("skipped")
                or report.get("todo")
                or report.get("flaky")
                or report.get("expected_failures")
            ):
                raise ValueError(
                    f"{name}: invalid runner/skip state before freezing: {diagnostic}"
                )
            if name == "backend":
                failure_names = re.findall(
                    r"^\s+name: ['\"]?([A-Za-z]+)['\"]?\s*$", diagnostic, re.M
                )
                valid_red = (
                    report.get("failed", 0) > 0
                    and len(failure_names) == report["failed"]
                    and set(failure_names) == {"AssertionError"}
                    and not re.search(
                        r"SQLITE_ERROR|ERR_MODULE|SyntaxError", diagnostic
                    )
                )
            else:
                invalid_failures = [
                    x
                    for x in failures
                    if not re.search(r"expect\(|AssertionError", x.split("\n", 1)[0])
                    or re.search(
                        r"E2E_RUNTIME_ERROR|E2E_NETWORK_ERROR|page.goto:|browserType.launch",
                        x.split("\n", 1)[0],
                    )
                ]
                valid_red = bool(failures) and not invalid_failures
            if not valid_red:
                raise ValueError(
                    f"{name}: need assertion RED, not setup/runtime failure. BEFORE each click/fill/check/selectOption await expect(THE_SAME_LOCATOR).toBeVisible() and toBeEnabled() as needed. Missing stub UI must fail at the assertion, never by action timeout. Preserve business assertions. "
                    + json.dumps(
                        {
                            "failures": (
                                invalid_failures if name != "backend" else failures
                            )[:4],
                            "output": diagnostic[:2000] if name == "backend" else None,
                        },
                        ensure_ascii=False,
                    )
                )
        self.frozen = self.test_hashes()
        if self.trace:
            self.trace.emit(
                "tests.freeze", files=self.frozen, requirement_ids=self.required_ids
            )
        return self.frozen
