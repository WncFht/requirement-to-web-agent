import os
import shutil
import subprocess
import time
from pathlib import Path

import pytest
from minisweagent.environments.local import LocalEnvironment
from minisweagent.exceptions import Submitted

from arc_adapter import SubmissionVerification
from progress import BashProgress

ROOT = Path(__file__).resolve().parents[1]
SUBMIT = {"command": "echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"}


@pytest.fixture
def gate(tmp_path):
    tools = tmp_path / "bin"
    tools.mkdir()
    npm = tools / "npm"
    npm.write_text(
        '#!/bin/sh\n'
        'echo "$*" >> "$VERIFY_LOG"\n'
        'case "$VERIFY_MODE" in\n'
        '  fail) echo "browser assertion failed"; exit 7;;\n'
        '  timeout) sleep 5;;\n'
        '  marker) echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT; exit 7;;\n'
        '  *) echo "checks passed";;\n'
        'esac\n'
    )
    npm.chmod(0o755)

    class Environment(SubmissionVerification, BashProgress, LocalEnvironment):
        pass

    env = Environment(cwd=str(tmp_path), timeout=2, env={
        "PATH": f"{tools}:{os.environ['PATH']}",
        "VERIFY_LOG": str(tmp_path / "verify.log"),
    })
    env.calllog_dir = tmp_path / "audit"
    return env, tmp_path / "verify.log"


def test_submission_rechecks_after_failure_and_on_each_retry(gate):
    env, log = gate
    env.config.env["VERIFY_MODE"] = "fail"
    result = env.execute(SUBMIT)
    assert result["returncode"] != 0
    assert "Submission blocked" in result["output"]
    assert "browser assertion failed" in result["output"]
    env.config.env["VERIFY_MODE"] = "pass"
    for _ in range(2):
        with pytest.raises(Submitted):
            env.execute(SUBMIT)
    assert log.read_text().splitlines() == ["run verify"] * 3


def test_failed_checks_cannot_submit_by_printing_marker(gate):
    env, _ = gate
    env.config.env["VERIFY_MODE"] = "marker"
    result = env.execute(SUBMIT)
    assert result["returncode"] == 1
    assert result["output"].startswith("Submission blocked")


def test_verification_timeout_returns_failure_within_run_budget(gate):
    env, _ = gate
    env.config.env["VERIFY_MODE"] = "timeout"
    env.verification_deadline = time.monotonic() + 0.15
    started = time.monotonic()
    result = env.execute(SUBMIT)
    assert time.monotonic() - started < 2
    assert result["returncode"] == 1
    assert "timed out" in result["output"]
    assert not env._verifying


def test_exhausted_budget_does_not_launch_checks(gate):
    env, log = gate
    env.verification_deadline = time.monotonic() - 1
    result = env.execute(SUBMIT)
    assert result["returncode"] == 1
    assert "budget is exhausted" in result["output"]
    assert not log.exists()


def test_ordinary_commands_do_not_trigger_checks(gate):
    env, log = gate
    assert env.execute({"command": "printf hello"})["output"] == "hello"
    assert not log.exists()


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is required")
@pytest.mark.parametrize("stage, expected", [
    ("missing", 1), ("build", 3), ("ui", 7), ("pass", 0),
])
def test_template_verification_propagates_failures(tmp_path, stage, expected):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    shutil.copy2(ROOT / "web_template/scripts/verify.mjs", scripts / "verify.mjs")
    tools = tmp_path / "bin"
    tools.mkdir()
    npm = tools / "npm"
    npm.write_text('#!/bin/sh\necho build >> stages.log\nexit "$BUILD_EXIT"\n')
    npm.chmod(0o755)
    if stage != "missing":
        checks = tmp_path / "verification"
        checks.mkdir()
        (checks / "ui.mjs").write_text(
            'import { appendFileSync } from "node:fs";\n'
            'appendFileSync("stages.log", "ui\\n");\n'
            f'process.exit({7 if stage == "ui" else 0});\n'
        )
    result = subprocess.run(
        [shutil.which("node"), str(scripts / "verify.mjs")],
        cwd=tmp_path, capture_output=True, text=True,
        env={**os.environ, "PATH": f"{tools}:{os.environ['PATH']}",
             "BUILD_EXIT": "3" if stage == "build" else "0"},
    )
    assert result.returncode == expected, result.stderr
    log = tmp_path / "stages.log"
    if stage == "missing":
        assert not log.exists()
        assert "Create verification/ui.mjs" in result.stderr
    else:
        assert log.read_text().splitlines() == (["build"] if stage == "build" else ["build", "ui"])
