"""Run the unchanged fixed fourteen browser checks against npm start and built assets."""

import argparse
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
from time import monotonic, sleep
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from accept_teacher import free_port, sha, verify_input
from infrastructure.utils.files import save_json
from infrastructure.utils.processes import (
    capture_process,
    npm_command,
    start_process,
    stop_process,
)
from infrastructure.utils.timing import timed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--attempt", default="initial")
    parser.add_argument("--fixed-attempt", default="initial")
    args = parser.parse_args()
    if not all(
        re.fullmatch(r"[a-z0-9][a-z0-9-]*", value)
        for value in (args.attempt, args.fixed_attempt)
    ):
        parser.error("Use lowercase letters/digits/hyphens for attempt names")
    output = args.output.resolve()
    manifest = verify_input()
    fixed = output / "frontend/tests" / ("fixed-" + args.fixed_attempt)
    summary = json.loads(
        (
            output / ".arc/teacher-acceptance" / args.fixed_attempt / "summary.json"
        ).read_text()
    )
    if summary["status"] != "GREEN" or not summary["all_preserved_gates_green"]:
        parser.error(
            "Complete all pipeline gates and fixed acceptance before production verification"
        )
    for name in ("context.ts", "setup.ts", "fixed.spec.ts"):
        if sha(fixed / name) != sha(ROOT / "acceptance" / name):
            parser.error("Frozen fixed assertion copy differs from source")
    for name, expected in manifest["files"].items():
        if (
            name.startswith("tests/")
            and sha(fixed / "teacher" / Path(name).name) != expected
        ):
            parser.error("Original teacher test copy differs from frozen source")
    if (
        not (output / "backend/dist/server.js").is_file()
        or not (output / "frontend/dist/index.html").is_file()
    ):
        parser.error("Production build is missing")
    result_dir = output / ".arc/production-acceptance" / args.attempt
    result_dir.mkdir(parents=True, exist_ok=False)
    port = free_port()
    with (
        timed("production_acceptance", output=output),
        TemporaryDirectory(prefix="teacher-acceptance-production-") as directory,
    ):
        temporary = Path(directory)
        database = str(temporary / "app.db")
        environment = {
            "DATABASE_URL": database,
            "ARC_E2E_DB_FILE": database,
            "PORT": str(port),
            "HOST": "127.0.0.1",
        }
        config = {
            "testDir": str(fixed),
            "globalSetup": str(fixed / "setup.ts"),
            "outputDir": str(result_dir / "test-results"),
            "workers": 1,
            "fullyParallel": False,
            "retries": 0,
            "forbidOnly": True,
            "timeout": 30000,
            "expect": {"timeout": 5000},
            "reporter": "json",
            "use": {"baseURL": f"http://127.0.0.1:{port}", "headless": True},
        }
        config_path = temporary / "production.config.mjs"
        config_path.write_text(
            "import { defineConfig } from "
            + json.dumps((output / "node_modules/@playwright/test/index.mjs").as_uri())
            + ";\nexport default defineConfig("
            + json.dumps(config)
            + ");\n"
        )
        with (result_dir / "server.log").open("w") as server_log:
            server = start_process(
                [*npm_command(), "start"],
                cwd=output,
                env=environment,
                stdout=server_log,
                stderr=server_log,
            )
            try:
                deadline = monotonic() + 30
                while True:
                    if server.poll() is not None:
                        raise ValueError(
                            "Production server exited before readiness; inspect server.log"
                        )
                    try:
                        with urlopen(
                            f"http://127.0.0.1:{port}/api/health", timeout=1
                        ) as response:
                            if response.status == 200:
                                break
                    except (URLError, TimeoutError):
                        pass
                    if monotonic() > deadline:
                        raise ValueError(
                            "Production server readiness timed out; inspect server.log"
                        )
                    sleep(0.1)
                result = capture_process(
                    [
                        "node",
                        "node_modules/@playwright/test/cli.js",
                        "test",
                        "--config",
                        str(config_path),
                    ],
                    cwd=output,
                    timeout=900,
                    env=environment,
                )
            finally:
                stop_process(server)
        (result_dir / "playwright.json").write_text(result["stdout"])
        (result_dir / "console.txt").write_text(result["output"])
        report = json.loads(result["stdout"])
        stats = report.get("stats", {})
        passed = (
            result["returncode"] == 0
            and stats.get("expected") == 14
            and not any(stats.get(key) for key in ("unexpected", "skipped", "flaky"))
            and not report.get("errors")
        )
        record = {
            "status": "GREEN" if passed else "FAILED",
            "mode": "npm start with production frontend/dist and backend/dist, isolated database; unchanged teacher4/fixed10 assertions",
            "stats": stats,
            "assertions_sha256": summary["assertions_sha256"],
            "input_sha256": summary["input_sha256"],
            "production_database_touched": False,
        }
        save_json(result_dir / "summary.json", record)
        print(json.dumps(record, indent=2))
        if not passed:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
