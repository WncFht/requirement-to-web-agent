"""ARC-Bench entrypoint for the Lab 6 numbered requirement compiler."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from infrastructure.utils.processes import child_environment
from infrastructure.utils.timing import timed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("requirement_path", type=Path)
    parser.add_argument("-o", "--output-dir", type=Path, required=True)
    parser.add_argument("--port", type=int, default=3000)
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Reuse verified pipeline completion records under unchanged provenance",
    )
    args = parser.parse_args()
    source = Path(__file__).resolve().parent
    inputs = args.requirement_path.expanduser().resolve()
    if inputs.is_file():
        if inputs.name != "requirements.yaml":
            parser.error("The input directory must contain requirements.yaml")
        inputs = inputs.parent
    if not (inputs / "requirements.yaml").is_file():
        parser.error("requirements.yaml was not found in the input directory")
    output = args.output_dir.expanduser().resolve()
    if output == inputs or output.is_relative_to(inputs):
        parser.error("Output directory must not equal or be inside the input directory")
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    engine = os.getenv("ARC_AGENT_ENGINE", "legacy")
    if engine not in {"legacy", "coding"}:
        parser.error("ARC_AGENT_ENGINE must be legacy or coding")
    if engine == "coding":
        from coding_agent.config import Config
        from coding_agent.loop import run

        result = run(Config.environment(inputs, output, args.port))
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "tokens": result["total_tokens"],
                    "output": str(output),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        if result["status"] != "INTERNAL_GREEN":
            parser.exit(
                1,
                f"Coding agent stopped: {result['status']}; inspect .arc/agent/result.json\n",
            )
        return
    if os.getenv("MODEL", "").lower().startswith("deepseek"):
        os.environ.setdefault("ARC_DISABLE_THINKING", "1")
    pipeline_command = [
        sys.executable,
        str(source / "run_all.py"),
        "--input",
        str(inputs),
        "--output",
        str(output),
    ]
    if args.resume:
        pipeline_command.append("--resume")
    with timed("entrypoint", output=output):
        build_application(pipeline_command, source, output, args.port)


def build_application(pipeline_command, source, output, port):
    subprocess.run(pipeline_command, cwd=source, check=True, env=child_environment())
    npm = (
        ["node", os.environ["npm_execpath"]]
        if os.environ.get("npm_execpath")
        else ["npm"]
    )
    for script, kind in (("db:init", "db_init"), ("build", "build")):
        with timed(kind, output=output, stage="finalize"):
            subprocess.run(
                [*npm, "run", script], cwd=output, check=True, env=child_environment()
            )
    deploy = output / "deploy.sh"
    deploy.write_text(
        "#!/usr/bin/env bash\nset -euo pipefail\n"
        'cd -- "$(dirname -- "${BASH_SOURCE[0]}")"\n'
        "npm install --include=dev --no-audit --no-fund\n"
        "npm run db:init\nnpm run build\n"
        f'export PORT="${{PORT:-{port}}}"\n'
        'export HOST="${HOST:-0.0.0.0}"\nexec npm start\n'
    )
    deploy.chmod(0o755)
    print(f"Lab 6 application built at {output}", flush=True)


if __name__ == "__main__":
    main()
