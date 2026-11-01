"""ARC-Bench entrypoint for the Lab 6 numbered requirement compiler."""

import argparse
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("requirement_path", type=Path)
    parser.add_argument("-o", "--output-dir", type=Path, required=True)
    parser.add_argument("--port", type=int, default=3000)
    parser.add_argument("--resume", action="store_true",
        help="Skip pipeline steps whose artifacts already exist (08/12 require status GREEN)")
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
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
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
    subprocess.run(pipeline_command, cwd=source, check=True)
    npm = (
        ["node", os.environ["npm_execpath"]]
        if os.environ.get("npm_execpath")
        else ["npm"]
    )
    subprocess.run([*npm, "run", "db:init"], cwd=output, check=True)
    subprocess.run([*npm, "run", "build"], cwd=output, check=True)
    deploy = output / "deploy.sh"
    deploy.write_text(
        "#!/usr/bin/env bash\nset -euo pipefail\n"
        'cd -- "$(dirname -- "${BASH_SOURCE[0]}")"\n'
        "npm install --include=dev --no-audit --no-fund\n"
        "npm run db:init\nnpm run build\n"
        f'export PORT="${{PORT:-{args.port}}}"\n'
        'export HOST="${HOST:-0.0.0.0}"\nexec npm start\n'
    )
    deploy.chmod(0o755)
    print(f"Lab 6 application built at {output}", flush=True)


if __name__ == "__main__":
    main()
