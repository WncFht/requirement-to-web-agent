"""Run an exact packaged revision in a fresh output directory (real model generation)."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dotenv import dotenv_values
from runtime.processes import start_process, stop_process
from package_agent import package


def prepare(inputs, output, port, environment):
    if not output:
        raise ValueError("OUT is required; choose a fresh output directory")
    inputs = Path(inputs).expanduser().resolve()
    if inputs.is_file() and inputs.name == "requirements.yaml":
        inputs = inputs.parent
    if not (inputs / "requirements.yaml").is_file():
        raise ValueError("INPUT must contain requirements.yaml")
    output = Path(output).expanduser().resolve()
    if output.exists():
        raise ValueError("OUT already exists; choose a fresh directory")
    if output.with_name(output.name + ".run.json").exists():
        raise ValueError("Run manifest already exists; choose a fresh directory")
    if output == inputs or output.is_relative_to(inputs):
        raise ValueError("OUT must be outside INPUT")
    if output == ROOT or output.is_relative_to(ROOT):
        raise ValueError("OUT must be outside the source repository")
    if not 1 <= port <= 65535:
        raise ValueError("PORT must be between 1 and 65535")
    if any(not environment.get(key) for key in ("OPENAI_API_KEY", "OPENAI_BASE_URL")):
        raise ValueError(
            "OPENAI_API_KEY and OPENAI_BASE_URL are required in environment or .env"
        )
    version = subprocess.check_output(
        ["node", "--version"], env=environment, text=True
    ).strip()
    if not version.startswith("v22."):
        raise ValueError("Node 22 is required; add its bin directory to PATH")
    return inputs, output


def run(ref, engine, inputs, output, port):
    environment = {
        key: value
        for key, value in {**dotenv_values(ROOT / ".env"), **os.environ}.items()
        if value is not None
    }
    inputs, output = prepare(inputs, output, port, environment)
    manifest = package(ref=ref, engine=engine)
    output.mkdir(parents=True, exist_ok=False)
    output.with_name(output.name + ".run.json").write_text(
        json.dumps(
            {
                key: manifest[key]
                for key in ("revision", "default_engine", "zip_sha256")
            },
            indent=2,
        )
        + "\n"
    )
    with TemporaryDirectory(prefix="lab6-submission-") as directory:
        source = Path(directory)
        with zipfile.ZipFile(manifest["zip_path"]) as archive:
            archive.extractall(source)
        process = start_process(
            [
                sys.executable,
                "main.py",
                str(inputs),
                "--output-dir",
                str(output),
                "--port",
                str(port),
            ],
            cwd=source,
            env=environment,
        )
        try:
            return process.wait()
        except BaseException:
            stop_process(process)
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default="HEAD")
    parser.add_argument("--engine", choices=("upstream", "coding"), default="upstream")
    parser.add_argument("--input", default="input")
    parser.add_argument("--output", required=True)
    parser.add_argument("--port", type=int, default=3000)
    args = parser.parse_args()
    try:
        code = run(args.ref, args.engine, args.input, args.output, args.port)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, str(error) + "\n")
    raise SystemExit(code)
