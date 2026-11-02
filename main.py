"""Platform adapter for the pinned upstream compiler or the independent coding agent."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from runtime.output import application_output
from runtime.processes import start_process, stop_process


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("requirement_path", type=Path)
    parser.add_argument("-o", "--output-dir", type=Path, required=True)
    parser.add_argument("--port", type=int, default=3000)
    parser.add_argument(
        "--model-log", "--debug-model-io", dest="model_log", action="store_true"
    )
    args = parser.parse_args(argv)
    source = Path(__file__).resolve().parent
    inputs = args.requirement_path.expanduser().resolve()
    if not (inputs / "requirements.yaml").is_file():
        parser.error("The input directory must contain requirements.yaml")
    if args.output_dir.expanduser().is_symlink():
        parser.error("Output directory cannot be a symlink")
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    engine = os.getenv("ARC_AGENT_ENGINE", "upstream")
    if engine not in {"upstream", "coding"}:
        parser.error(
            "ARC_AGENT_ENGINE must be upstream or coding; historical legacy uses a fixed Git tag"
        )
    output = args.output_dir.expanduser().resolve()
    try:
        with application_output(output, inputs=inputs, source=source) as workspace:
            generate_application(
                source, inputs, workspace, args.port, engine, args.model_log
            )
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Generation failed: {error}\n")


def generate_application(source, inputs, output, port, engine, model_log=False):
    if engine == "coding":
        from coding_agent.config import Config
        from coding_agent.loop import run

        result = run(Config.environment(inputs, output, port))
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "tokens": result["total_tokens"],
                    "output": str(output),
                }
            ),
            flush=True,
        )
        if result["status"] != "INTERNAL_GREEN":
            raise RuntimeError(
                f"Coding agent stopped: {result['status']}; inspect .arc/agent/result.json"
            )
        return
    command = [
        sys.executable,
        str(source / "upstream/main.py"),
        str(inputs),
        "--output-dir",
        str(output),
        "--port",
        str(port),
    ]
    if model_log:
        command.append("--model-log")
    environment = dict(os.environ)
    environment["MODEL"] = environment.get("MODEL") or "deepseek-flash"
    # Separate interpreters preserve upstream's original imports and coding's support modules.
    process = start_process(command, cwd=source / "upstream", env=environment)
    try:
        code = process.wait()
    except BaseException:
        stop_process(process)
        raise
    if code:
        raise subprocess.CalledProcessError(code, command)
    # Upstream main returns 0 on some failures; the platform needs a real failure signal.
    report = output / ".arc/compilation.json"
    if not report.is_file() or json.loads(report.read_text()).get("status") != "GREEN":
        raise RuntimeError(
            "Upstream compilation was not GREEN; inspect .arc/compilation.json"
        )
    if not all(
        (output / name).exists()
        for name in ("package.json", "deploy.sh", "frontend", "backend")
    ):
        raise RuntimeError("Upstream application is missing required deployment files")


if __name__ == "__main__":
    main()
