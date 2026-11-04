"""Verify/materialize frozen ARC-Bench inputs and run public tests locally, offline."""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
from urllib.parse import urlsplit
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DEFAULT_SNAPSHOT = ROOT / "benchmarks/arc-bench/2026-11-05"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def relative(name):
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or "\\" in name or not path.parts:
        raise ValueError("Unsafe snapshot path: " + name)
    return Path(*path.parts)


def load(snapshot):
    snapshot = Path(snapshot).resolve()
    manifest = json.loads((snapshot / "manifest.json").read_text())
    if manifest.get("schema_version") != 1:
        raise ValueError("Unsupported snapshot schema")
    return snapshot, manifest


def verify(snapshot=DEFAULT_SNAPSHOT, text_only=False):
    snapshot, manifest = load(snapshot)
    actual = {str(p.relative_to(snapshot)) for p in snapshot.rglob("*") if p.is_file()}
    if actual != set(manifest["files"]) | {"manifest.json"}:
        raise ValueError("Snapshot member set differs from manifest")
    checked = 0
    for name, expected in manifest["files"].items():
        path = snapshot / relative(name)
        if text_only and expected["kind"] in {
            "official_archive",
            "compressed_public_client",
            "public_client",
        }:
            continue
        if (
            path.is_symlink()
            or not path.is_file()
            or not path.resolve().is_relative_to(snapshot)
        ):
            raise ValueError("Missing or unsafe snapshot member: " + name)
        if path.stat().st_size != expected["bytes"] or sha(path) != expected["sha256"]:
            with path.open("rb") as stream:
                pointer = stream.read(80).startswith(
                    b"version https://git-lfs.github.com/spec/v1"
                )
            if pointer:
                raise ValueError("Git LFS object missing; run git lfs pull: " + name)
            raise ValueError("Snapshot hash mismatch: " + name)
        checked += 1
    for task in manifest["tasks"]:
        metadata = json.loads((snapshot / relative(task["metadata"])).read_text())
        if (
            metadata["requirements_yaml"].encode()
            != (snapshot / task["input_yaml"]).read_bytes()
        ):
            raise ValueError("API/ZIP requirements differ: " + task["task_id"])
        if not task["tests_available"]:
            continue
        response = json.loads((snapshot / relative(task["test_response"])).read_text())
        for item in response["files"]:
            path = snapshot / relative(task["acceptance"]) / relative(item["path"])
            if path.read_bytes() != item["content"].encode():
                raise ValueError("Exported assertion differs from API: " + str(path))
    return {
        "status": "VERIFIED",
        "files": checked,
        "tasks": len(manifest["tasks"]),
        "text_only": text_only,
    }


def fresh(output):
    output = Path(output).expanduser().resolve()
    if output.exists():
        raise ValueError("Refusing to overwrite output: " + str(output))
    if output.is_relative_to(ROOT) and not output.is_relative_to(ROOT / "work"):
        raise ValueError("Repository outputs must be under ignored work/")
    return output


def task_record(manifest, task_id):
    matches = [task for task in manifest["tasks"] if task["task_id"] == task_id]
    if len(matches) != 1:
        raise ValueError("Unknown or ambiguous task: " + task_id)
    return matches[0]


def extract(archive, output, prefix=None):
    """Extract only regular members below an optional task prefix; reject zip traversal."""
    with zipfile.ZipFile(archive) as bundle:
        if sum(m.file_size for m in bundle.infolist()) > 2 * 1024**3:
            raise ValueError("Archive is too large to materialize")
        for member in bundle.infolist():
            path = relative(member.filename)
            if stat.S_ISLNK(member.external_attr >> 16):
                raise ValueError("Archive symlink: " + member.filename)
            if prefix:
                if not path.parts or path.parts[0] != prefix:
                    continue
                path = Path(*path.parts[1:])
            if member.is_dir() or str(path) == ".":
                continue
            target = output / path
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(bundle.read(member))
            mode = (member.external_attr >> 16) & 0o777
            if mode:
                target.chmod(mode)


def materialize(task_id, output, snapshot=DEFAULT_SNAPSHOT):
    snapshot, manifest = load(snapshot)
    verify(snapshot)
    task = task_record(manifest, task_id)
    output = fresh(output)
    output.mkdir(parents=True)
    extract(snapshot / task["reference_archive"], output / "input", prefix=task_id)
    if sha(output / "input/requirements.yaml") != task["requirements_sha256"]:
        raise ValueError("Materialized input hash differs")
    if task["tests_available"]:
        shutil.copytree(snapshot / task["acceptance"], output / "acceptance")
    # Public API text is kept separate from the exact downloadable input ZIP.
    shutil.copytree(snapshot / "tasks" / task_id / "docs", output / "docs")
    record = {
        "task_id": task_id,
        "snapshot_manifest_sha256": sha(snapshot / "manifest.json"),
        "published_test_count": task["platform_test_count"],
        "tests_available": task["tests_available"],
        "inputs_and_assertions": {
            str(p.relative_to(output)): sha(p)
            for p in sorted(output.rglob("*"))
            if p.is_file()
        },
        "model_calls": 0,
        "tests_executed": False,
    }
    (output / "materialization.json").write_text(json.dumps(record, indent=2) + "\n")
    return output, record


def starter(language, output, snapshot=DEFAULT_SNAPSHOT):
    snapshot, manifest = load(snapshot)
    verify(snapshot)
    archive = next(
        (
            a
            for a in manifest["archives"]
            if a["kind"] == "starter" and a["language"] == language
        ),
        None,
    )
    if not archive:
        raise ValueError("Starter language not available")
    output = fresh(output)
    output.mkdir(parents=True)
    extract(snapshot / archive["path"], output)
    return {
        "status": "MATERIALIZED",
        "output": str(output),
        "language": language,
        "executed": False,
    }


def test_count(report):
    def visit(suite):
        return sum(len(spec.get("tests", [])) for spec in suite.get("specs", [])) + sum(
            visit(s) for s in suite.get("suites", [])
        )

    return sum(visit(suite) for suite in report.get("suites", []))


def report_status(report, returncode, collect, published):
    count = test_count(report)
    valid = (
        returncode == 0
        and not report.get("errors")
        and count == published
        and count > 0
    )
    if collect:
        return "COLLECTED" if valid else "FAILED"
    stats = report.get("stats", {})
    valid = (
        valid
        and stats.get("expected") == count
        and not any(stats.get(k) for k in ["skipped", "unexpected", "flaky"])
    )
    return "LOCAL_PUBLIC_TESTS_GREEN" if valid else "FAILED"


def public_tests(
    task_id,
    output,
    dependencies,
    *,
    base_url="http://127.0.0.1:3000",
    collect=True,
    snapshot=DEFAULT_SNAPSHOT,
):
    snapshot, manifest = load(snapshot)
    task = task_record(manifest, task_id)
    if not task["tests_available"]:
        raise ValueError(
            "Official acceptance source is not exposed for this task; no local substitute is scored"
        )
    parsed = urlsplit(base_url)
    if (
        parsed.scheme not in {"http", "https"}
        or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError(
            "Local test URL must be loopback-only, without credentials or query"
        )
    dependencies = Path(dependencies).expanduser().resolve()
    cli = dependencies / "@playwright/test/cli.js"
    if not cli.is_file():
        raise ValueError(
            "Supply an existing node_modules with @playwright/test; no automatic install"
        )
    node = shutil.which("node")
    if not node:
        raise ValueError("Node.js is required")
    output, record = materialize(task_id, output, snapshot)
    (output / "node_modules").symlink_to(dependencies, target_is_directory=True)
    config = {
        "testDir": "./acceptance",
        "testMatch": "**/*.spec.ts",
        "timeout": 30000,
        "workers": 1,
        "retries": 0,
        "forbidOnly": True,
        "outputDir": "./test-results",
        "use": {"baseURL": base_url, "trace": "retain-on-failure"},
    }
    (output / "playwright.config.cjs").write_text(
        "module.exports = " + json.dumps(config) + ";\n"
    )
    command = [
        node,
        str(cli),
        "test",
        "--config",
        str(output / "playwright.config.cjs"),
        "--reporter=json",
    ]
    if collect:
        command.append("--list")
    # The runner does not initialize a model client or load any credential file.
    from runtime.processes import capture_process

    environment = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith(("OPENAI_", "VISUAL_", "ARC_AGENT_"))
        and k not in {"MODEL", "DATABASE_URL"}
    }
    try:
        result = capture_process(
            command, cwd=output, timeout=180 if collect else 7200, env=environment
        )
    except subprocess.TimeoutExpired:
        result = {
            "returncode": 124,
            "output": "Local Playwright deadline exceeded; owned processes stopped",
        }
    (output / "runner.stdout").write_text(result.get("stdout", result["output"]))
    try:
        report = json.loads(result.get("stdout", result["output"]))
    except ValueError:
        report = {"errors": [{"message": result["output"][-8000:]}]}
    (output / "playwright-report.json").write_text(json.dumps(report, indent=2) + "\n")
    actual = {
        str(p.relative_to(output)): sha(p)
        for p in output.rglob("*")
        if p.is_file()
        and (
            p.is_relative_to(output / "input")
            or p.is_relative_to(output / "acceptance")
            or p.is_relative_to(output / "docs")
        )
    }
    if actual != record["inputs_and_assertions"]:
        raise ValueError(
            "Inputs or official assertions changed during local test operation"
        )
    count = test_count(report)
    status = report_status(
        report, result["returncode"], collect, record["published_test_count"]
    )
    receipt = {
        "status": status,
        "task_id": task_id,
        "collected_tests": count,
        "published_test_count": record["published_test_count"],
        "returncode": result["returncode"],
        "tests_executed": not collect,
        "assertions_unchanged": True,
        "stats": report.get("stats"),
        "node": subprocess.check_output([node, "--version"], text=True).strip(),
        "playwright": json.loads(
            (dependencies / "@playwright/test/package.json").read_text()
        )["version"],
        "snapshot_manifest_sha256": record["snapshot_manifest_sha256"],
        "local_configuration": config,
        "parity": "Public-source contract only; not a platform score or exact environment replica",
        "limitations": [
            "Application startup, seed state and server clock must be prepared separately",
            "Actual platform container, runtime options, hidden tests and scoring are not available",
        ],
    }
    (output / "result.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("verify")
    check.add_argument("--text-only", action="store_true")
    commands.add_parser("list")
    copy = commands.add_parser("materialize")
    copy.add_argument("task")
    copy.add_argument("--output", type=Path, required=True)
    blank = commands.add_parser("starter")
    blank.add_argument(
        "--language", choices=["python", "javascript", "typescript"], default="python"
    )
    blank.add_argument("--output", type=Path, required=True)
    for name in ("collect", "test"):
        cmd = commands.add_parser(name)
        cmd.add_argument("task")
        cmd.add_argument("--output", type=Path, required=True)
        cmd.add_argument("--dependencies", type=Path, required=True)
        cmd.add_argument("--base-url", default="http://127.0.0.1:3000")
    args = parser.parse_args(argv)
    try:
        if args.command == "verify":
            result = verify(args.snapshot, args.text_only)
        elif args.command == "list":
            _, manifest = load(args.snapshot)
            result = [
                {k: t[k] for k in ["task_id", "platform_test_count", "tests_available"]}
                for t in manifest["tasks"]
            ]
        elif args.command == "materialize":
            _, result = materialize(args.task, args.output, args.snapshot)
        elif args.command == "starter":
            result = starter(args.language, args.output, args.snapshot)
        else:
            result = public_tests(
                args.task,
                args.output,
                args.dependencies,
                base_url=args.base_url,
                collect=args.command == "collect",
                snapshot=args.snapshot,
            )
        print(json.dumps(result, indent=2))
        return 1 if isinstance(result, dict) and result.get("status") == "FAILED" else 0
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as error:
        parser.exit(1, str(error) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
