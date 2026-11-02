"""Cookie evidence must be observed, immutable, cached by backend content, and checked before freezing."""

import json
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from infrastructure.stages.frontend.interactions.cookie_transport import (
    COOKIE_GUARD_SOURCE,
    REPORT,
    observe_cookie_transport,
)
from infrastructure.stages.frontend.interactions.testing import validate_e2e_source


class CookieTransportTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        files = {
            "backend/src/register.ts": "export async function handle() {}",
            "backend/tests/register.test.ts": "// original immutable assertion",
            "backend/tests/support/apis.ts": "// original compiler bindings",
            ".arc/implementation_paths.json": json.dumps(
                {"api": {"register": "backend/src/register.ts"}}
            ),
        }
        for name, text in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        (self.root / "node_modules").mkdir()
        self.apis = {"register": {"signature": {"name": "registerAccount"}}}
        self.calls = []
        self.names = [""]
        self.bindings = None

    def execute(self, command, *, cwd, timeout):
        self.calls.append(command)
        if command[-1] == "--version":
            return {"returncode": 0, "stdout": "v22.23.2\n", "output": ""}
        if "--test" in command:
            self.assertNotEqual(Path(cwd), self.root)
            self.bindings = (Path(cwd) / "backend/tests/support/apis.ts").read_text()
            self.assertEqual(
                (Path(cwd) / "backend/tests/register.test.ts").read_text(),
                "// original immutable assertion",
            )
            return {"returncode": 0, "stdout": "", "output": ""}
        return {
            "returncode": 0,
            "stdout": json.dumps(
                {
                    "status": "OBSERVED" if self.names else "NO_STORED_COOKIES",
                    "names": self.names,
                    "producers": {},
                    "node": "v22.23.2",
                }
            ),
            "output": "",
        }

    def test_real_backend_bindings_are_wrapped_only_in_disposable_mirror(self):
        before = {
            path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()
        }
        with patch(
            "infrastructure.stages.frontend.interactions.cookie_transport.capture_process",
            side_effect=self.execute,
        ):
            result = observe_cookie_transport(self.root, self.apis)
        self.assertEqual(result["names"], [""])
        self.assertIn("original0(request, connection)", self.bindings)
        self.assertIn("export async function registerAccount", self.bindings)
        for path, value in before.items():
            self.assertEqual(path.read_bytes(), value)
        self.assertTrue((self.root / REPORT).is_file())

    def test_backend_content_change_invalidates_cached_observation(self):
        with patch(
            "infrastructure.stages.frontend.interactions.cookie_transport.capture_process",
            side_effect=self.execute,
        ):
            first = observe_cookie_transport(self.root, self.apis)
            self.calls.clear()
            self.assertEqual(observe_cookie_transport(self.root, self.apis), first)
            self.assertEqual(
                len(self.calls), 1
            )  # Runtime identity checked; tests/browser are cached.
            (self.root / "backend/src/register.ts").write_text("// backend changed")
            self.names = ["session_id"]
            changed = observe_cookie_transport(self.root, self.apis)
        self.assertNotEqual(first["fingerprint"], changed["fingerprint"])
        self.assertEqual(changed["names"], ["session_id"])

    def test_unknown_cookie_is_distinct_from_an_observed_empty_name(self):
        self.names = []
        with patch(
            "infrastructure.stages.frontend.interactions.cookie_transport.capture_process",
            side_effect=self.execute,
        ):
            result = observe_cookie_transport(self.root, self.apis)
        self.assertEqual(result["names"], [])
        self.assertEqual(result["status"], "NO_STORED_COOKIES")

    def test_failed_backend_probe_never_publishes_evidence(self):
        def failed(command, **kwargs):
            if "--test" in command:
                return {"returncode": 1, "output": "assertion failure"}
            return self.execute(command, **kwargs)

        with patch(
            "infrastructure.stages.frontend.interactions.cookie_transport.capture_process",
            side_effect=failed,
        ):
            with self.assertRaisesRegex(ValueError, "Backend assertions failed"):
                observe_cookie_transport(self.root, self.apis)
        self.assertFalse((self.root / REPORT).exists())

    def test_no_api_does_not_run_probe(self):
        with patch(
            "infrastructure.stages.frontend.interactions.cookie_transport.capture_process"
        ) as execute:
            self.assertEqual(
                observe_cookie_transport(self.root, {})["status"], "NO_APIS"
            )
            execute.assert_not_called()

    def test_literal_guard_supports_empty_name_and_rejects_historical_mismatch(self):
        source = 'test("valid session restores user",async()=>{await page.context().addCookies([{name:"credential",value:"credential",url:baseURL!}]);});'
        with self.assertRaisesRegex(ValueError, "tested backend producers"):
            validate_e2e_source(source, [""])
        validate_e2e_source(source.replace('name:"credential"', 'name:""'), [""])

    def test_actual_runtime_guard_checks_dynamic_helper_arguments_and_restores_method(
        self,
    ):
        # Erase type annotations only; the body exercised here is the production helper.
        javascript = re.sub(r"^import type[^\n]+\n", "", COOKIE_GUARD_SOURCE)
        javascript = javascript.replace(
            "context: BrowserContext, title: string, names: string[]",
            "context, title, names",
        )
        runner = (
            javascript
            + r"""
const results=[];
for(const [title,names,cookieName,reject] of [
 ['valid session restores user',[''],'credential',true],
 ['valid session restores user',[''],'',false],
 ['existing session restores user',['session_id'],'session',true],
 ['seeded session restores user',['session_id'],'session_id',false],
 ['unknown session shows logged-out',['session_id'],'unknown',false],
 ['valid session restores user',[],'guessed',true],
]) {
 let calls=0;const context={addCookies:async function(cookies){if(this!==context)throw Error('lost binding');calls++;return 'unchanged';}};
 const original=context.addCookies;
 const restore=installCookieGuard(context,title,names);
 let rejected=false;try{await context.addCookies([{name:[cookieName].join(''),value:'fixture'}]);}
 catch(error){if(!String(error).includes('E2E_FIXTURE_COOKIE_MISMATCH'))throw error;rejected=true;}
 restore();
 if(rejected!==reject || calls!==(reject?0:1) || context.addCookies!==original) throw Error('guard result mismatch');
 results.push({rejected,calls});
}
console.log(JSON.stringify(results));
"""
        )
        result = subprocess.run(
            ["node", "--input-type=module", "-"],
            input=runner,
            text=True,
            capture_output=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(json.loads(result.stdout)), 6)
