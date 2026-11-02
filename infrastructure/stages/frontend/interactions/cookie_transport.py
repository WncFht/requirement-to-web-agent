"""Observe tested backend Cookie producers in Chromium before freezing E2E fixtures."""

from hashlib import sha256
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

from infrastructure.shared.project.entrypoints import import_path
from infrastructure.stages.backend.runtime import TEST_BINDINGS_PATH, api_entrypoint
from infrastructure.utils.files import save_json
from infrastructure.utils.processes import capture_process
from infrastructure.utils.timing import timed

REPORT = ".arc/backend_cookie_transport.json"

BROWSER_PROBE = r"""
import { createServer } from 'node:http';
import { readFileSync } from 'node:fs';
import { chromium } from '@playwright/test';
const records=readFileSync(process.argv[2],'utf8').trim().split('\n').filter(Boolean).map(line=>JSON.parse(line));
const server=createServer((request,response)=>{
 const record=records[Number(request.url.slice(1))];
 response.setHeader('Set-Cookie',record.headers);response.end('cookie transport probe');
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
let browser;
const producers={};
try{
 browser=await chromium.launch({headless:true});
 for(let index=0;index<records.length;index++){
  const context=await browser.newContext();
  try{
   const page=await context.newPage();
   await page.goto(`http://127.0.0.1:${server.address().port}/${index}`);
   const names=(await context.cookies()).map(cookie=>cookie.name);
   const producer=producers[records[index].api]??={samples:0,names:[],not_stored:0};
   producer.samples++;
   producer.names=[...new Set([...producer.names,...names])].sort();
   if(!names.length) producer.not_stored++;
  }finally{await context.close();}
 }
 const names=[...new Set(Object.values(producers).flatMap(producer=>producer.names))].sort();
 console.log(JSON.stringify({status:names.length?'OBSERVED':'NO_STORED_COOKIES',names,producers,node:process.version}));
}finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
"""


def _files(output):
    files = []
    for directory in ("backend/src", "backend/tests"):
        files.extend(path for path in (output / directory).rglob("*") if path.is_file())
    for relative in (
        "package-lock.json",
        "backend/package.json",
        "backend/tsconfig.json",
        "backend/tsconfig.test.json",
    ):
        if (output / relative).is_file():
            files.append(output / relative)
    if any(
        path.is_symlink() or not path.resolve().is_relative_to(output) for path in files
    ):
        raise ValueError("Cookie observation refuses symlinked/escaped backend files")
    return sorted(files)


def _bindings(output, apis, capture):
    lines = ['import { appendFileSync } from "node:fs";']
    for number, (aid, api) in enumerate(apis.items()):
        entry = api_entrypoint(output, aid)
        if entry is None:
            raise ValueError(f"Cannot observe unimplemented backend API: {aid}")
        lines.extend(
            [
                f"import {{ {entry['export']} as original{number} }} from {json.dumps(import_path(TEST_BINDINGS_PATH, entry['path']))};",
                f"export async function {api['signature']['name']}(request, connection) {{",
                f"  const result = await original{number}(request, connection);",
                "  if(result.status >= 200 && result.status < 300) {",
                '    const headers=Object.entries(result.headers??{}).filter(([key])=>key.toLowerCase()==="set-cookie").flatMap(([,value])=>Array.isArray(value)?value:[value]);',
                f'    if(headers.length) appendFileSync({json.dumps(str(capture))}, JSON.stringify({{api:{json.dumps(aid)},headers}})+"\\n");',
                "  }",
                "  return result;",
                "}",
            ]
        )
    return "\n".join(lines) + "\n"


def observe_cookie_transport(output, apis):
    """Replay immutable backend assertions in a disposable mirror and inspect real browser storage.

    Only test bindings in the mirror are wrapped; original source/tests and the
    production DB remain untouched. The report stores names, hashes and counts,
    never credentials. No observed names is unknown, not a guessed empty name.
    """
    output = Path(output).resolve()
    if not apis:
        return {"status": "NO_APIS", "names": [], "producers": {}}
    files = _files(output)
    hashes = {
        path.relative_to(output).as_posix(): sha256(path.read_bytes()).hexdigest()
        for path in files
    }
    node = capture_process(["node", "--version"], cwd=output, timeout=10)[
        "stdout"
    ].strip()
    fingerprint = sha256(
        json.dumps(
            {"files": hashes, "apis": apis, "node": node}, sort_keys=True
        ).encode()
    ).hexdigest()
    destination = output / REPORT
    if destination.is_file():
        saved = json.loads(destination.read_text(encoding="utf-8-sig"))
        if saved.get("version") == 1 and saved.get("fingerprint") == fingerprint:
            return saved
    tests = [
        path.relative_to(output).as_posix()
        for path in files
        if path.as_posix().endswith(".test.ts")
        and path.is_relative_to(output / "backend/tests")
    ]
    if not tests:
        raise ValueError("Cookie transport observation needs the passing backend tests")
    with (
        timed("cookie_transport_probe", output=output),
        TemporaryDirectory(prefix="arc-cookie-transport-") as temporary,
    ):
        root = Path(temporary)
        for path in files:
            target = root / path.relative_to(output)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
        # Reuse read-only dependencies; no npm install and no model call.
        (root / "node_modules").symlink_to(
            output / "node_modules", target_is_directory=True
        )
        (root / "package.json").write_text('{"type":"module"}\n')
        capture = root / "captured-cookies.jsonl"
        capture.write_text("")
        (root / TEST_BINDINGS_PATH).write_text(_bindings(output, apis, capture))
        tested = capture_process(
            ["node", "--import", "tsx", "--test", *tests], cwd=root, timeout=180
        )
        if tested["returncode"]:
            raise ValueError(
                "Backend assertions failed in isolated Cookie observation; no transport evidence accepted. "
                + tested["output"][-1500:]
            )
        runner = root / "observe.mjs"
        runner.write_text(BROWSER_PROBE)
        observed = capture_process(
            ["node", str(runner), str(capture)], cwd=root, timeout=60
        )
        if observed["returncode"]:
            raise ValueError(
                "Chromium could not observe backend Cookie storage; no transport evidence accepted. "
                + observed["output"][-1500:]
            )
        evidence = {
            "version": 1,
            "fingerprint": fingerprint,
            **json.loads(observed["stdout"]),
            "backend_files_sha256": hashes,
        }
        save_json(destination, evidence)
        return evidence


COOKIE_GUARD_SOURCE = r"""import type { BrowserContext } from "@playwright/test";
export function installCookieGuard(context: BrowserContext, title: string, names: string[]) {
  const positive=/\b(valid|existing|seeded|authenticated)\s+(session|cookie)\b/i.test(title);
  const negative=/\b(invalid|unknown|unrecognized|expired|missing)\s+(session|cookie|credential)\b/i.test(title);
  if(!positive || negative) return () => {};
  const original=context.addCookies;
  context.addCookies=async function(cookies) {
    if(!cookies.some(cookie=>names.includes(cookie.name))) {
      throw new Error("E2E_FIXTURE_COOKIE_MISMATCH: Positive session setup must use a Cookie name observed from the tested backend in Chromium: " + JSON.stringify(names) + ". Empty string means an actual empty name, not an unknown name. If no name was observed, establish the session through the real registration/login API instead of guessing. Repair this fixture before freezing; production handlers must remain unchanged.");
    }
    return original.call(this,cookies);
  };
  return () => {context.addCookies=original;};
}
"""
