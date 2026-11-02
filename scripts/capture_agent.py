"""Capture production pages against an isolated database without editing the application."""

import argparse
import json
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from coding_agent.acceptance import execute, servers
from coding_agent.trace import file_manifest, json_write

SCRIPT = """import {chromium} from '@playwright/test';
const browser=await chromium.launch({headless:true}), errors=[];
try {const page=await browser.newPage({baseURL:process.argv[1],viewport:JSON.parse(process.argv[3])});
page.on('pageerror',e=>errors.push(e.message));
for(const [i,path] of JSON.parse(process.argv[4]).entries()){
await page.goto(path);await page.waitForLoadState('networkidle');
await page.screenshot({path:process.argv[2]+'/'+i+'.png',fullPage:true});
}console.log(JSON.stringify({errors}));}finally{await browser.close();}"""


def capture(output, evidence, routes, viewport):
    output, evidence = Path(output).resolve(), Path(evidence).resolve()
    if any(not route.startswith("/") or route.startswith("//") for route in routes):
        raise ValueError("Routes must be local absolute paths")
    before = file_manifest(output, logs=True)
    evidence.mkdir(parents=True, exist_ok=False)
    with TemporaryDirectory(prefix="coding-visual-") as tmp:
        with servers(output, Path(tmp), "production") as (base, env):
            observed = execute(
                output,
                [
                    "node",
                    "--input-type=module",
                    "-e",
                    SCRIPT,
                    base,
                    str(evidence),
                    json.dumps(viewport),
                    json.dumps(routes),
                ],
                env=env,
            )
            if observed["returncode"]:
                raise ValueError(observed["output"])
        for log in Path(tmp).glob("server-*.log"):
            shutil.copyfile(log, evidence / log.name)
    unchanged = before == file_manifest(output, logs=True)
    result = {
        "output": str(output),
        "mode": "production",
        "viewport": viewport,
        "routes": routes,
        "application_unchanged": unchanged,
        "application_sha256": before,
        "browser": json.loads(observed["stdout"]),
        "files": file_manifest(evidence, logs=True),
        "scope": "Human visual review only; not a quantitative similarity score or a new primary success result.",
    }
    json_write(evidence / "source.json", result)
    if not unchanged:
        raise ValueError("Application changed while capturing")
    return {k: v for k, v in result.items() if k not in {"application_sha256", "files"}}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("output", type=Path)
    p.add_argument("--evidence", type=Path, required=True)
    p.add_argument("--routes", nargs="+", default=["/"])
    p.add_argument("--width", type=int, default=1423)
    p.add_argument("--height", type=int, default=900)
    a = p.parse_args()
    print(
        json.dumps(
            capture(
                a.output, a.evidence, a.routes, {"width": a.width, "height": a.height}
            )
        )
    )
