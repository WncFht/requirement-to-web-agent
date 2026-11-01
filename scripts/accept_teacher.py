"""Run unchanged teacher browser tests plus frozen independent behavior checks."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from infrastructure.stages.frontend.interactions.e2e_runtime import CONFIG_SOURCE
from infrastructure.utils.processes import capture_process

ALIASES = {
    "username": {"username"},
    "password_hash": {"passwordhash", "hashedpassword"},
    "nationality": {"nationality"},
    "name": {"name", "fullname"},
    "passport_number": {"passportnumber", "passport"},
    "passport_expiration_date": {
        "passportexpirationdate",
        "passportexpirydate",
        "passportexpiration",
    },
    "date_of_birth": {"dateofbirth", "birthdate", "dob"},
    "gender": {"gender"},
    "email": {"email", "emailaddress"},
    "agreement_consent": {"agreementconsent", "agreementaccepted", "agreedtoterms"},
}


def normalized(value):
    return re.sub(r"[^a-z0-9]", "", value.lower())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_input():
    manifest = json.loads((ROOT / "input/source.json").read_text())
    for relative, expected in manifest["files"].items():
        if sha(ROOT / "input" / relative) != expected:
            raise ValueError(f"Teacher input changed: {relative}")
    return manifest


def make_adapter(output):
    schema = json.loads((output / ".arc/db_schema.json").read_text())["entities"]
    candidates = []
    for name, entity in schema.items():
        fields = entity["fields"]
        roles = {}
        for role, aliases in ALIASES.items():
            matches = [field for field in fields if normalized(field) in aliases]
            if len(matches) == 1:
                roles[role] = matches[0]
        if len(roles) == len(ALIASES):
            candidates.append((name, fields, roles))
    if len(candidates) != 1:
        raise ValueError(
            "Ambiguous account schema; review and provide --adapter instead of skipping checks"
        )
    account_name, fields, roles = candidates[0]
    ids = [name for name, field in fields.items() if field["primary_key"]]
    if len(ids) != 1:
        raise ValueError("Expected one account primary key; provide a reviewed adapter")
    account_id = (
        1
        if fields[ids[0]]["type"] == "integer"
        else "11111111-1111-4111-8111-111111111111"
    )
    values = {
        "username": "taken_traveler",
        "password_hash": "computed-by-fixed-fixture",
        "nationality": "Vietnam",
        "name": "Existing Traveler",
        "passport_number": "P-existing-001",
        "passport_expiration_date": "2099-12-31",
        "date_of_birth": "1995-06-15",
        "gender": "Male",
        "email": "taken.traveler@example.com",
        "agreement_consent": 1,
    }
    seed = {roles[role]: value for role, value in values.items()} | {ids[0]: account_id}
    for field, spec in fields.items():
        if field not in seed:
            if not spec["nullable"]:
                raise ValueError(
                    f"Unknown required account field: {field}; provide a reviewed adapter"
                )
            seed[field] = None
    sessions = []
    for name, entity in schema.items():
        fks = [
            field
            for field, spec in entity["fields"].items()
            if spec.get("references") == account_name + "." + ids[0]
        ]
        credentials = [
            field
            for field in entity["fields"]
            if normalized(field)
            in {"credential", "sessioncredential", "token", "sessiontoken"}
        ]
        if len(fks) == 1 and len(credentials) == 1:
            sessions.append((name, entity["fields"], fks[0], credentials[0]))
    if len(sessions) != 1:
        raise ValueError("Ambiguous session schema; provide a reviewed adapter")
    session_name, session_fields, owner, credential = sessions[0]
    token = "33333333-3333-4333-8333-333333333333"
    session_seed = {owner: account_id, credential: token}
    for field, spec in session_fields.items():
        if field in session_seed:
            continue
        if spec["primary_key"]:
            session_seed[field] = (
                1
                if spec["type"] == "integer"
                else "22222222-2222-4222-8222-222222222222"
            )
        elif spec["nullable"]:
            session_seed[field] = None
        else:
            raise ValueError(
                f"Unknown required session field: {field}; provide a reviewed adapter"
            )
    apis = json.loads((output / ".arc/backend_apis.json").read_text())["apis"]
    paths = [
        api["signature"]["path"]
        for api in apis.values()
        if api["signature"]["method"] == "GET"
        and ("session" in json.dumps(api).lower())
    ]
    cookies = set()
    for path in (output / "backend/src").rglob("*.ts"):
        text = path.read_text()
        for match in re.finditer(r"(?:[`\"'])([a-zA-Z_][a-zA-Z0-9_-]*)=\$\{", text):
            cookies.add(match.group(1))
    if len(cookies) != 1 or len(paths) != 1:
        raise ValueError(
            f"Cannot identify unique session cookie/path: cookies={sorted(cookies)}, paths={paths}; provide --adapter"
        )
    return {
        "account_table": account_name,
        "account_fields": roles,
        "account_seed": seed,
        "session_table": session_name,
        "session_seed": session_seed,
        "session_token": token,
        "cookie_name": cookies.pop(),
        "session_path": paths[0],
        "evidence": {
            "schema_sha256": sha(output / ".arc/db_schema.json"),
            "apis_sha256": sha(output / ".arc/backend_apis.json"),
        },
    }


def free_port():
    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        return server.getsockname()[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--adapter", type=Path)
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Diagnostic run only; never marks stable",
    )
    args = parser.parse_args()
    output = args.output.resolve()
    manifest = verify_input()
    result_dir = output / ".arc/teacher-acceptance"
    result_dir.mkdir(parents=True, exist_ok=True)
    adapter = (
        json.loads(args.adapter.read_text()) if args.adapter else make_adapter(output)
    )
    tests = output / "frontend/tests/fixed"
    if tests.exists():
        raise ValueError(
            "Fixed acceptance evidence exists; archive it explicitly before rerunning"
        )
    tests.mkdir()
    shutil.copytree(ROOT / "input/tests", tests / "teacher")
    for name in ["context.ts", "setup.ts", "fixed.spec.ts"]:
        shutil.copy2(ROOT / "acceptance" / name, tests / name)
    (tests / "adapter.json").write_text(json.dumps(adapter, indent=2) + "\n")
    (result_dir / "adapter.json").write_text(json.dumps(adapter, indent=2) + "\n")
    for relative, expected in manifest["files"].items():
        if (
            relative.startswith("tests/")
            and sha(tests / "teacher" / Path(relative).name) != expected
        ):
            raise ValueError("Teacher test copy mismatch")
    config = CONFIG_SOURCE.replace(
        'testDir: "./tests/e2e"',
        'testDir: "./tests/fixed", globalSetup: "./tests/fixed/setup.ts"',
    ).replace('outputDir: "./test-results/e2e"', 'outputDir: "./test-results/fixed"')
    (output / "frontend/playwright.fixed.config.ts").write_text(config)
    first, second = free_port(), free_port()
    while first == second:
        second = free_port()
    with TemporaryDirectory(prefix="teacher-acceptance-") as temporary:
        env = {
            **os.environ,
            "ARC_E2E_BACKEND_PORT": str(first),
            "ARC_E2E_FRONTEND_PORT": str(second),
            "ARC_E2E_DB_FILE": str(Path(temporary) / "app.db"),
        }
        result = capture_process(
            [
                "node",
                "node_modules/@playwright/test/cli.js",
                "test",
                "--config",
                "frontend/playwright.fixed.config.ts",
            ],
            cwd=output,
            timeout=900,
            env=env,
        )
    (result_dir / "playwright.json").write_text(result["stdout"])
    (result_dir / "console.txt").write_text(result["output"])
    try:
        report = json.loads(result["stdout"])
    except ValueError as error:
        raise ValueError(
            "Independent Playwright did not return JSON; inspect console.txt"
        ) from error
    stats = report.get("stats", {})
    gates = {}
    for name in ["backend_tdd.json", "ui_checks.json", "frontend_e2e.json"]:
        path = output / ".arc" / name
        gates[name] = (
            json.loads(path.read_text()).get("status") if path.exists() else None
        )
    green = (
        result["returncode"] == 0
        and stats.get("expected") == 14
        and not any(stats.get(key) for key in ["unexpected", "skipped", "flaky"])
        and not report.get("errors")
    )
    summary = {
        "status": "GREEN" if green else "FAILED",
        "stats": stats,
        "teacher_test_count": 4,
        "fixed_test_count": 10,
        "input_sha256": manifest["files"]["requirements.yaml"],
        "assertions_sha256": {
            path.name: sha(path) for path in (ROOT / "acceptance").glob("*.ts")
        },
        "preserved_gates": gates,
        "diagnostic_only": args.allow_incomplete,
        "all_preserved_gates_green": all(value == "GREEN" for value in gates.values()),
    }
    (result_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    if not green:
        raise SystemExit(1)
    if not args.allow_incomplete and not summary["all_preserved_gates_green"]:
        raise SystemExit("Independent checks passed but pipeline gates are incomplete")


if __name__ == "__main__":
    main()
