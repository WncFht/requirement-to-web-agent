"""ARC-Bench-compatible entry for an unchanged mini-SWE-agent engine."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from arc_adapter import build_task, prepare_output, run_agent
from build_info import write_run_build_info
from progress import emit, failure, redact, variable_presence


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "requirement_path",
        type=Path,
        help="Directory containing requirements.yaml and reference/",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        required=True,
        help="Generated application directory (existing files are preserved)",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("ARC_MODEL")
        or os.environ.get("MODEL")
        or "deepseek-flash",
    )
    parser.add_argument(
        "--max-steps", type=int, default=int(os.environ.get("ARC_MAX_STEPS", "250"))
    )
    parser.add_argument(
        "--max-seconds",
        type=int,
        default=int(os.environ.get("ARC_MAX_SECONDS", "3600")),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate input and stage template; no API calls",
    )
    args = parser.parse_args(argv)
    if args.max_steps < 1 or args.max_seconds < 1:
        parser.error("--max-steps and --max-seconds must be positive")
    return args


def main(argv: list[str] | None = None) -> int:
    started = time.monotonic()
    from dotenv import load_dotenv

    # Collected before load_dotenv: this reports what the PLATFORM injected, while
    # override=False guarantees the platform always wins over the project .env below.
    injected = variable_presence()
    load_dotenv(Path(__file__).resolve().parent / ".env", override=False)
    args = parse_args(argv)
    try:
        if not args.dry_run:
            emit("entry_start", injected_variables_present=injected)
        if not args.dry_run and (
            not os.environ.get("OPENAI_BASE_URL")
            or not os.environ.get("OPENAI_API_KEY")
        ):
            raise RuntimeError(
                "Set OPENAI_BASE_URL and OPENAI_API_KEY before running the model"
            )
        checked = prepare_output(args.requirement_path, args.output_dir)
        build = write_run_build_info(
            Path(__file__).resolve().parent, args.output_dir,
            configuration={"model": args.model,
                           "reasoning_effort_override": os.environ.get("ARC_REASONING_EFFORT"),
                           "max_steps": args.max_steps, "max_seconds": args.max_seconds},
        )
        emit("build_info", **{key: build.get(key) for key in (
            "commit", "tags", "dirty", "source_sha256", "origin", "matches_build",
            "runtime_source_sha256", "changed_files", "run_configuration",
        )})
        info = {
            "input": str(args.requirement_path.resolve()),
            "output": str(args.output_dir.resolve()),
            "reference_images": len(checked["images"]),
            "requirements_bytes": len(checked["raw_yaml"].encode("utf-8")),
        }
        if args.dry_run:
            # Exercise identical multimodal task preparation without exposing base64 payloads.
            prompt = build_task(checked, args.requirement_path.resolve())
            info["multimodal_image_parts"] = prompt.count("<MSWEA_MULTIMODAL_CONTENT>")
            info["status"] = "dry_run_only_no_generation"
            print(json.dumps(info, ensure_ascii=False), flush=True)
            return 0
        print(
            json.dumps({**info, "status": "running_model"}, ensure_ascii=False),
            flush=True,
        )
        result = run_agent(
            checked,
            args.requirement_path.resolve(),
            args.output_dir,
            args.model,
            args.max_steps,
            args.max_seconds,
        )
        result["build_info"] = {key: build.get(key) for key in (
            "commit", "tags", "dirty", "source_sha256", "origin", "matches_build",
            "runtime_source_sha256",
        )}
        (args.output_dir / ".arc_adapter/run_summary.json").write_text(
            json.dumps(result, indent=2), encoding="utf-8"
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["status"] == "Submitted" else 1
    except Exception as exc:
        failure("entry_error", exc, started)
        print(redact(f"ARC-Bench adapter error: {exc}"), file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
