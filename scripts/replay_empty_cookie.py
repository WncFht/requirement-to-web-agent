"""Replay the timing run's Cookie mismatch using real handlers and Chromium, without editing it."""

import argparse
import hashlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from infrastructure.utils.processes import capture_process

PROBE = r"""
import { createServer } from 'node:http';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
const root = process.cwd();
const moduleAt = p => import(pathToFileURL(resolve(root, p)).href);
const {chromium} = await moduleAt('node_modules/@playwright/test/index.mjs');
const {createDatabaseClient} = await moduleAt('backend/src/db/client.ts');
const {initializeDatabase} = await moduleAt('backend/src/db/initialize.ts');
const {registerAccount, getHomepageSession} = await moduleAt('backend/tests/support/apis.ts');
const db = createDatabaseClient(':memory:');
initializeDatabase(db);
const username='cookie_probe_traveler';
const body={username,name:'Traveler One',nationality:'Vietnam',passportNumber:'P1234567',
passportExpirationDate:'2030-12-31',dateOfBirth:'1990-05-05',gender:'Male',
email:'probe@example.com',password:'correct-horse',confirmPassword:'correct-horse',agreementConsent:true};
const server=createServer(async (request,response)=>{
 try{
  const apiRequest={params:{},query:{},body:request.url==='/bootstrap'?body:{},headers:request.headers};
  const result=await (request.url==='/bootstrap'?registerAccount:getHomepageSession)(apiRequest,db);
  response.statusCode=result.status;
  for(const [key,value] of Object.entries(result.headers??{})) response.setHeader(key,value);
  response.setHeader('Content-Type','application/json');response.end(JSON.stringify(result.body));
 }catch{response.statusCode=500;response.end('{}');}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const base=`http://127.0.0.1:${server.address().port}`;
const browser=await chromium.launch({headless:true});
try{
 const first=await browser.newContext();const page=await first.newPage();
 const registered=await page.goto(base+'/bootstrap');
 const cookies=await first.cookies();
 const credential=db.prepare('SELECT credential FROM "Session"').get().credential;
 await page.goto(base+'/session');const natural=JSON.parse(await page.textContent('body'));
 const wrong=await browser.newContext();
 await wrong.addCookies([{name:credential,value:credential,url:base}]);
 const wrongPage=await wrong.newPage();await wrongPage.goto(base+'/session');
 const negative=JSON.parse(await wrongPage.textContent('body'));
 const matching=await browser.newContext();
 await matching.addCookies([{name:'',value:credential,url:base}]);
 const matchingPage=await matching.newPage();await matchingPage.goto(base+'/session');
 const positive=JSON.parse(await matchingPage.textContent('body'));
 const result={scope:'Actual generated register/session handlers, isolated memory DB, real Chromium; frozen tests and application source unchanged',
 registration_status:registered.status(),
 natural_browser:{cookie_count:cookies.length,cookie_names:cookies.map(c=>c.name),authenticated:natural.authenticated,username_matches:natural.username===username},
 generated_fixture_shape:{name_equals_value:true,authenticated:negative.authenticated},
 matching_empty_name_fixture:{authenticated:positive.authenticated,username_matches:positive.username===username}};
 console.log(JSON.stringify(result));
 if(registered.status()!==201 || cookies.length!==1 || cookies[0].name!=='' || natural.authenticated!==true || negative.authenticated!==false || positive.authenticated!==true)process.exitCode=1;
}finally{await browser.close();await new Promise(resolve=>server.close(resolve));db.close();}
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Refusing to overwrite replay evidence")
    root = args.run.resolve()
    files = [
        ".arc/implementation_paths.json",
        ".arc/backend_contracts.json",
        "backend/src/register-account.ts",
        "backend/src/api/get-homepage-session.ts",
        "frontend/tests/e2e/req-1-homepage-session.spec.ts",
    ]
    hashes = {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in files
    }
    with TemporaryDirectory(prefix="arc-empty-cookie-") as temporary:
        runner = Path(temporary) / "probe.mjs"
        runner.write_text(PROBE)
        result = capture_process(
            ["node", "--import", "tsx", str(runner)], cwd=root, timeout=60
        )
    evidence = {
        "returncode": result["returncode"],
        "files_sha256": hashes,
        "result": json.loads(result["stdout"]) if result["stdout"].strip() else None,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
    if result["returncode"]:
        parser.exit(1, "Cookie replay failed; inspect isolated runtime/dependencies.\n")
    print(json.dumps(evidence["result"], indent=2))


if __name__ == "__main__":
    main()
