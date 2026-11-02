"""Engine-independent execution of the unchanged teacher/fixed oracle in a mirror."""

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
from time import monotonic, sleep
from urllib.error import URLError
from urllib.request import urlopen

from coding_agent.checks import application_environment
from coding_agent.protocol import green
from coding_agent.trace import audit, file_manifest, json_write, sha
from infrastructure.utils.processes import start_process, stop_process, process_options
from scripts.accept_teacher import ALIASES, normalized, free_port, verify_input

ROOT = Path(__file__).resolve().parents[1]

SCHEMA = r"""import Database from 'better-sqlite3';
import {pathToFileURL} from 'node:url';
const {initializeDatabase}=await import(pathToFileURL(process.cwd()+'/backend/src/db/initialize.ts').href);
const db=new Database(process.argv[1]??':memory:');initializeDatabase(db);
const quote=n=>'"'+n.replaceAll('"','""')+'"',out={};
for(const row of db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").all()){
 const fks=db.prepare('PRAGMA foreign_key_list('+quote(row.name)+')').all();
 out[row.name]={sample:db.prepare('SELECT * FROM '+quote(row.name)+' LIMIT 1').get()??null,fields:Object.fromEntries(db.prepare('PRAGMA table_info('+quote(row.name)+')').all().map(c=>[c.name,{type:/INT/i.test(c.type)?'integer':'string',primary_key:!!c.pk,nullable:!c.notnull&&!c.pk,default:c.dflt_value,references:fks.some(f=>f.from===c.name)?(()=>{const f=fks.find(f=>f.from===c.name);return f.table+'.'+f.to})():null}]))};
}db.close();console.log(JSON.stringify(out));"""

PROBE = r"""import {chromium} from '@playwright/test';
import {pathToFileURL} from 'node:url';
const {entry,openRegistration,fillRegistration,button,newAccount}=await import(pathToFileURL(process.argv[3]).href);
const browser=await chromium.launch({headless:true});
try{const context=await browser.newContext({baseURL:process.argv[2]});const page=await context.newPage();
 const paths=new Set();let home=true;
 page.on('request',r=>{const p=new URL(r.url()).pathname;if(home&&r.method()==='GET'&&p.startsWith('/api/')&&p!=='/api/health')paths.add(p)});
 await entry(page);await page.waitForLoadState('networkidle');home=false;
 await openRegistration(page);await fillRegistration(page,newAccount());await button(page,'Next step').click();
 await page.waitForURL(new URL('/',process.argv[2]).href,{timeout:10000});await page.waitForLoadState('networkidle');
 const cookies=await context.cookies();
 console.log(JSON.stringify({names:[...new Set(cookies.map(c=>c.name))],cookies:cookies.map(c=>({name:c.name,value:c.value})),paths:[...paths]}));
}finally{await browser.close();}"""


def execute(output, args, *, timeout=300, env=None):
    process = subprocess.Popen(
        args,
        cwd=output,
        env=application_environment(env),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        **process_options(),
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except BaseException:
        stop_process(process)
        raise
    return {
        "returncode": process.returncode,
        "stdout": stdout,
        "output": (stdout + stderr)[-24000:],
    }


def adapter_from_schema(schema, transport):
    """Map storage locations only; immutable fixtures retain all expected business values."""
    aliases_by_role = {role: set(aliases) for role, aliases in ALIASES.items()}
    aliases_by_role["agreement_consent"].update(
        {"agreement", "agreed", "termsaccepted"}
    )
    aliases_by_role["passport_expiration_date"].update(
        {"passportexpiry", "passportexpirydate"}
    )
    candidates = []
    for table, entity in schema.items():
        fields = entity["fields"]
        roles = {}
        for role, aliases in aliases_by_role.items():
            matches = [name for name in fields if normalized(name) in aliases]
            if len(matches) == 1:
                roles[role] = matches[0]
        if len(roles) == len(ALIASES):
            candidates.append((table, fields, roles))
    if len(candidates) != 1:
        raise ValueError("Ambiguous actual account schema; no assertions skipped")
    account_table, fields, roles = candidates[0]
    keys = [n for n, f in fields.items() if f["primary_key"]]
    if len(keys) != 1:
        raise ValueError("Account primary key is ambiguous")
    account_id = (
        1
        if fields[keys[0]]["type"] == "integer"
        else "11111111-1111-4111-8111-111111111111"
    )
    expected = {
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
    account_seed = {roles[k]: v for k, v in expected.items()} | {keys[0]: account_id}
    for name, field in fields.items():
        if name not in account_seed:
            if field["nullable"]:
                account_seed[name] = None
            elif normalized(name) in {
                "createdat",
                "updatedat",
                "createdon",
                "updatedon",
            } and schema[account_table].get("sample", {}):
                account_seed[name] = schema[account_table]["sample"][name]
            elif field.get("default") is None:
                raise ValueError("Unknown required account field: " + name)
    sessions = []
    for name, entity in schema.items():
        sf = entity["fields"]
        owners = [
            n for n, f in sf.items() if f["references"] == account_table + "." + keys[0]
        ]
        credentials = [
            n
            for n in sf
            if normalized(n)
            in {
                "credential",
                "sessioncredential",
                "token",
                "sessiontoken",
                "tokenhash",
                "sessiontokenhash",
                "credentialhash",
                "sessionhash",
            }
        ]
        if not credentials:
            # A session's sole text primary key may itself be the opaque cookie.
            credentials = [
                n for n, f in sf.items() if f["primary_key"] and f["type"] == "string"
            ]
        if len(owners) == len(credentials) == 1:
            sessions.append((name, sf, owners[0], credentials[0]))
    if len(sessions) != 1:
        raise ValueError("Ambiguous actual session schema")
    table, sf, owner, credential = sessions[0]
    token = "33333333-3333-4333-8333-333333333333"
    stored_token = token
    if normalized(credential).endswith("hash"):
        cookies = transport.get("cookies", [])
        sample = schema[table].get("sample") or {}
        if (
            len(cookies) != 1
            or sample.get(credential)
            != hashlib.sha256(cookies[0]["value"].encode()).hexdigest()
        ):
            raise ValueError(
                "Session hash encoding not proved by actual cookie and stored registration"
            )
        stored_token = hashlib.sha256(token.encode()).hexdigest()
    session_seed = {owner: account_id, credential: stored_token}
    for name, field in sf.items():
        if name in session_seed:
            continue
        if field["primary_key"]:
            session_seed[name] = (
                1
                if field["type"] == "integer"
                else "22222222-2222-4222-8222-222222222222"
            )
        elif field["nullable"]:
            session_seed[name] = None
        elif normalized(name) in {
            "createdat",
            "updatedat",
            "expiresat",
            "createdon",
            "expireson",
        } and schema[table].get("sample", {}):
            session_seed[name] = schema[table]["sample"][name]
        elif field.get("default") is None:
            raise ValueError("Unknown required session field: " + name)
    if len(transport["names"]) != 1 or len(transport["paths"]) != 1:
        raise ValueError(
            "Actual browser transport is ambiguous: " + json.dumps(transport)
        )
    return {
        "account_table": account_table,
        "account_fields": roles,
        "account_seed": account_seed,
        "session_table": table,
        "session_seed": session_seed,
        "session_token": token,
        "cookie_name": transport["names"][0],
        "session_path": transport["paths"][0],
    }


@contextmanager
def servers(output, directory, mode):
    back, front = free_port(), free_port()
    while front == back:
        front = free_port()
    database = str(directory / "app.db")
    env = {
        "DATABASE_URL": database,
        "ARC_E2E_DB_FILE": database,
        "PORT": str(back),
        "HOST": "127.0.0.1",
    }
    processes = []
    streams = []
    try:
        commands = (
            [([shutil.which("node"), "--import", "tsx", "backend/src/server.ts"], back)]
            if mode == "fixed"
            else [([shutil.which("npm"), "start"], back)]
        )
        if mode == "fixed":
            commands.append(
                (
                    [
                        shutil.which("node"),
                        "../node_modules/vite/bin/vite.js",
                        "--config",
                        "vite.e2e.config.ts",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        str(front),
                        "--strictPort",
                    ],
                    front,
                )
            )
        for number, (command, port) in enumerate(commands):
            stream = (directory / f"server-{number}.log").open("w")
            streams.append(stream)
            cwd = output / "frontend" if number else output
            child = subprocess.Popen(
                command,
                cwd=cwd,
                env=application_environment(
                    env | {"ARC_BACKEND_URL": f"http://127.0.0.1:{back}"}
                ),
                stdout=stream,
                stderr=stream,
                **process_options(),
            )
            processes.append(child)
            deadline = monotonic() + 30
            while True:
                if child.poll() is not None:
                    raise ValueError("Acceptance service exited; inspect server logs")
                try:
                    with urlopen(
                        f"http://127.0.0.1:{port}"
                        + ("/api/health" if number == 0 else "/"),
                        timeout=1,
                    ) as r:
                        if r.status == 200:
                            break
                except (URLError, TimeoutError):
                    pass
                if monotonic() > deadline:
                    raise ValueError("Acceptance service readiness timeout")
                sleep(0.1)
        yield f"http://127.0.0.1:{front if mode == 'fixed' else back}", env
    finally:
        for child in reversed(processes):
            stop_process(child)
        for stream in streams:
            stream.close()


def internal_green(output):
    record = Path(output) / ".arc/agent/result.json"
    if record.exists():
        proof = audit(output)
        return (
            proof["valid"]
            and proof["result"]["status"] == "INTERNAL_GREEN"
            and set(proof["result"]["checks"])
            == {"typecheck", "backend", "ui", "e2e", "build"}
            and all(green(v) for v in proof["result"]["checks"].values())
        )
    return all(
        json.loads((Path(output) / ".arc" / f"{n}.json").read_text()).get("status")
        == "GREEN"
        for n in ("backend_tdd", "ui_checks", "frontend_e2e")
    )


@contextmanager
def evaluation_directory(evidence):
    """Retain service logs even if readiness, transport probing or evaluation fails."""
    with TemporaryDirectory(prefix="independent-acceptance-") as tmp:
        owner = Path(tmp)
        try:
            yield owner
        finally:
            for log in owner.glob("server-*.log"):
                shutil.copy2(log, evidence / log.name)


def evaluate(output, evidence, mode="fixed", adapter=None):
    output, evidence = Path(output).resolve(), Path(evidence).resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    verify_input()
    before = file_manifest(output, logs=True)
    if not internal_green(output):
        raise ValueError(
            "Internal gates/evidence are incomplete; no fake legacy GREEN receipts"
        )
    with evaluation_directory(evidence) as owner:
        mirror = owner / "mirror"
        mirror.mkdir()
        (mirror / "package.json").write_text('{"type":"module"}\n')
        (mirror / "node_modules").symlink_to(
            output / "node_modules", target_is_directory=True
        )
        (mirror / "backend").mkdir()
        (mirror / "backend/src").symlink_to(
            output / "backend/src", target_is_directory=True
        )
        (mirror / "backend/tests").symlink_to(
            output / "backend/tests", target_is_directory=True
        )
        tests = mirror / "frontend/tests/fixed"
        tests.mkdir(parents=True)
        shutil.copytree(ROOT / "input/tests", tests / "teacher")
        for name in ("context.ts", "setup.ts", "fixed.spec.ts"):
            shutil.copy2(ROOT / "acceptance" / name, tests / name)
        assertions = {
            p.relative_to(tests).as_posix(): sha(p) for p in tests.rglob("*.ts")
        }
        for relative, digest in assertions.items():
            original = (
                ROOT / "input/tests" / relative[8:]
                if relative.startswith("teacher/")
                else ROOT / "acceptance" / relative
            )
            if sha(original) != digest:
                raise ValueError("Frozen assertion copy changed")
        with servers(output, owner, mode) as (base_url, env):
            if adapter is None:
                schema = execute(
                    output,
                    [
                        shutil.which("node"),
                        "--import",
                        "tsx",
                        "--input-type=module",
                        "-e",
                        SCHEMA,
                    ],
                )
                if schema["returncode"]:
                    raise ValueError(schema["output"])
                probe = output / "node_modules/.cache/coding-accept-probe.mjs"
                probe.parent.mkdir(parents=True, exist_ok=True)
                probe.write_text(PROBE)
                observed = execute(
                    output,
                    [
                        shutil.which("node"),
                        "--import",
                        "tsx",
                        str(probe),
                        base_url,
                        str(tests / "teacher/helpers.ts"),
                    ],
                    timeout=60,
                )
                if observed["returncode"]:
                    raise ValueError(
                        "Browser transport probe failed: " + observed["output"]
                    )
                schema = execute(
                    output,
                    [
                        shutil.which("node"),
                        "--import",
                        "tsx",
                        "--input-type=module",
                        "-e",
                        SCHEMA,
                        str(owner / "app.db"),
                    ],
                )
                if schema["returncode"]:
                    raise ValueError(schema["output"])
                adapter = adapter_from_schema(
                    json.loads(schema["stdout"]), json.loads(observed["stdout"])
                )
                json_write(
                    evidence / "schema.json",
                    {
                        key: {"fields": value["fields"]}
                        for key, value in json.loads(schema["stdout"]).items()
                    },
                )
                observed_public = json.loads(observed["stdout"])
                observed_public.pop("cookies", None)
                json_write(evidence / "transport.json", observed_public)
            json_write(tests / "adapter.json", adapter)
            json_write(evidence / "adapter.json", adapter)
            config = {
                "testDir": str(tests),
                "globalSetup": str(tests / "setup.ts"),
                "outputDir": str(evidence / "test-results"),
                "workers": 1,
                "fullyParallel": False,
                "retries": 0,
                "forbidOnly": True,
                "timeout": 30000,
                "expect": {"timeout": 5000},
                "reporter": "json",
                "use": {"baseURL": base_url, "headless": True},
            }
            config_path = owner / "accept.config.mjs"
            config_path.write_text(
                "import {defineConfig} from "
                + json.dumps(
                    (output / "node_modules/@playwright/test/index.mjs").as_uri()
                )
                + ";\nexport default defineConfig("
                + json.dumps(config)
                + ");\n"
            )
            tested = execute(
                mirror,
                [
                    shutil.which("node"),
                    str(output / "node_modules/@playwright/test/cli.js"),
                    "test",
                    "--config",
                    str(config_path),
                ],
                env=env,
                timeout=900,
            )
            (evidence / "playwright.json").write_text(tested["stdout"])
            (evidence / "console.txt").write_text(tested["output"])
            raw = json.loads(tested["stdout"])
            stats = raw.get("stats", {})
    unchanged = before == file_manifest(output, logs=True)
    passed = (
        tested["returncode"] == 0
        and stats.get("expected") == 14
        and not any(stats.get(k) for k in ("unexpected", "skipped", "flaky"))
        and not raw.get("errors")
        and unchanged
    )
    result = {
        "status": "GREEN" if passed else "FAILED",
        "stats": stats,
        "assertions_sha256": assertions,
        "application_unchanged": unchanged,
        "mode": mode,
        "internal_gates_green": True,
    }
    json_write(evidence / "summary.json", result)
    return result


def evaluate_notes(output, evidence, mode="fixed"):
    """Independent second-task oracle, frozen before paid notes generation."""
    output, evidence = Path(output).resolve(), Path(evidence).resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    if not internal_green(output):
        raise ValueError("Internal gates incomplete")
    before = file_manifest(output, logs=True)
    oracle = ROOT / "experiments/notes-oracle/fixed.spec.ts"
    with evaluation_directory(evidence) as owner:
        mirror = owner / "mirror"
        mirror.mkdir()
        (mirror / "package.json").write_text('{"type":"module"}')
        (mirror / "node_modules").symlink_to(
            output / "node_modules", target_is_directory=True
        )
        (mirror / "backend").mkdir()
        (mirror / "backend/src").symlink_to(
            output / "backend/src", target_is_directory=True
        )
        tests = mirror / "frontend/tests/fixed"
        tests.mkdir(parents=True)
        shutil.copyfile(oracle, tests / "fixed.spec.ts")
        with servers(output, owner, mode) as (base_url, env):
            config = {
                "testDir": str(tests),
                "outputDir": str(evidence / "test-results"),
                "workers": 1,
                "fullyParallel": False,
                "retries": 0,
                "forbidOnly": True,
                "timeout": 30000,
                "expect": {"timeout": 5000},
                "reporter": "json",
                "use": {"baseURL": base_url, "headless": True},
            }
            cfg = owner / "notes.config.mjs"
            cfg.write_text(
                "import {defineConfig} from "
                + json.dumps(
                    (output / "node_modules/@playwright/test/index.mjs").as_uri()
                )
                + ";\nexport default defineConfig("
                + json.dumps(config)
                + ");\n"
            )
            tested = execute(
                mirror,
                [
                    shutil.which("node"),
                    str(output / "node_modules/@playwright/test/cli.js"),
                    "test",
                    "--config",
                    str(cfg),
                ],
                env=env,
                timeout=900,
            )
            (evidence / "playwright.json").write_text(tested["stdout"])
            (evidence / "console.txt").write_text(tested["output"])
            raw = json.loads(tested["stdout"])
            stats = raw.get("stats", {})
    unchanged = before == file_manifest(output, logs=True)
    passed = (
        tested["returncode"] == 0
        and stats.get("expected") == 5
        and not any(stats.get(k) for k in ("unexpected", "skipped", "flaky"))
        and not raw.get("errors")
        and unchanged
    )
    result = {
        "status": "GREEN" if passed else "FAILED",
        "stats": stats,
        "oracle_sha256": sha(oracle),
        "application_unchanged": unchanged,
        "mode": mode,
        "internal_gates_green": True,
    }
    json_write(evidence / "summary.json", result)
    return result
