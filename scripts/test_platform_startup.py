"""Check an extracted ZIP against a populated platform output without any model request."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from coding_agent.support.shared.project.initialize import initialize_project
from package_agent import inspect_package

GUARD = """import json,os,socket,sys
from pathlib import Path
from openai import OpenAI

def forbidden(*args, **kwargs):
    raise RuntimeError("OFFLINE_NETWORK_FORBIDDEN")
socket.socket.connect = forbidden
socket.socket.connect_ex = forbidden

def boundary(self, *args, **kwargs):
    Path(os.environ["OFFLINE_BOUNDARY_RECORD"]).write_text(json.dumps({"argv":sys.argv,"model_client_blocked":True}))
    raise RuntimeError("OFFLINE_MODEL_BOUNDARY")
OpenAI.__init__ = boundary
"""


def hashes(root):
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def verify(package, output):
    manifest = inspect_package(package)
    directory = Path(output).resolve()
    directory.mkdir(parents=True, exist_ok=False)
    source, inputs, target = (
        directory / name for name in ("submission", "requirements-source", "template")
    )
    with zipfile.ZipFile(package) as archive:
        archive.extractall(source)
    inputs.mkdir()
    (inputs / "requirements.yaml").write_text(
        "id: REQ-1\nname: Offline\nchildren: []\n"
    )
    initialize_project(target)
    (target / "platform-trace.json").write_text('{"requirements":3,"scenarios":2}\n')
    initial = hashes(target)
    guard = directory / "guard"
    guard.mkdir()
    (guard / "sitecustomize.py").write_text(GUARD)
    boundary = directory / "model-boundary.json"
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("OPENAI_", "VISUAL_", "ARC_"))
        and key not in {"MODEL", "PYTHONPATH", "PYTHONSTARTUP"}
    } | {
        "PYTHONPATH": str(guard),
        "OPENAI_BASE_URL": "http://127.0.0.1:1/v1",
        "OPENAI_API_KEY": "offline-placeholder-not-a-real-key",
        "OFFLINE_BOUNDARY_RECORD": str(boundary),
    }
    with (directory / "startup.log").open("w") as log:
        done = subprocess.run(
            [
                sys.executable,
                str(source / "main.py"),
                str(inputs),
                "--output-dir",
                str(target),
            ],
            cwd=source,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=45,
        )
    log = (directory / "startup.log").read_text()
    if not boundary.is_file():
        raise ValueError(
            "Agent did not reach the blocked model boundary; see "
            + str(directory / "startup.log")
        )
    match = re.search(r"Initial platform output detected; generating in (.+)", log)
    if not match:
        raise ValueError("Platform output was not staged")
    application = Path(match.group(1))
    if hashes(target) != initial:
        raise ValueError("Failed startup modified the initial platform output")
    stage_zero = None
    if manifest["default_engine"] == "legacy":
        state = json.loads((application / ".arc/pipeline_state.json").read_text())
        stage_zero = state["completed"][:1] == ["00_project_initialization.py"]
        if not stage_zero:
            raise ValueError(
                "Legacy Stage 00 did not complete before the offline boundary"
            )
    elif manifest["default_engine"] == "upstream":
        state = json.loads((application / ".arc/compilation.json").read_text())
        stage_zero = (
            state["stages"].get("00_project_initialization", {}).get("status")
            == "GREEN"
        )
        if not stage_zero:
            raise ValueError(
                "Upstream Stage 00 did not complete before the offline boundary"
            )
    elif not (application / "frontend/playwright.agent.config.ts").is_file():
        raise ValueError("Coding application initialization did not complete")
    result = {
        "revision": manifest["revision"],
        "engine": manifest["default_engine"],
        "startup_contract_passed": True,
        "generation_complete": False,
        "expected_generation_returncode": done.returncode,
        "model_client_blocked_before_request": True,
        "real_model_requests": 0,
        "initial_output_unchanged": True,
        "initialization_passed": stage_zero if stage_zero is not None else True,
        "retained_workspace": str(application),
    }
    if (
        done.returncode == 0
        or "OFFLINE_MODEL_BOUNDARY" not in log
        or "OFFLINE_NETWORK_FORBIDDEN" in log
    ):
        raise ValueError("Unexpected offline boundary result")
    (directory / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.package, args.output), indent=2))
