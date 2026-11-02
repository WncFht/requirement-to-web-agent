"""Exercise generated read-only mount handlers before expensive browser regressions."""

import json
from tempfile import TemporaryDirectory
from pathlib import Path

from infrastructure.shared.project.entrypoints import implementation_entrypoint
from infrastructure.stages.frontend.interactions.design import api_ids
from infrastructure.utils.processes import capture_process

RUNNER = r"""import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
const config = JSON.parse(readFileSync(process.argv[2], "utf8"));
const results = [];
for (const subject of config.subjects) {
  for (const mode of ["http-503", "transport-rejection"]) {
    let calls = 0, updates = 0, timer;
    const data = structuredClone(config.defaults);
    try {
      const module = await import(pathToFileURL(subject.path).href);
      const context = {
        get data() { return data; }, input: {}, trigger: subject.trigger,
        update(patch) { Object.assign(data, patch); updates += 1; },
        navigate() {},
        async api() {
          calls += 1;
          if (mode === "transport-rejection") throw new Error("Compiler read-only transport failure");
          return { status: 503, body: { error: "Compiler read-only lookup failure" }, headers: {} };
        },
      };
      await Promise.race([
        Promise.resolve().then(() => module[subject.export](context)),
        new Promise((_, reject) => { timer = setTimeout(() => reject(new Error("Read-only handler did not settle")), 3000); }),
      ]);
      results.push({ event: subject.event, mode, calls, updates, status: calls ? "PASSED" : "NOT_EXERCISED" });
    } catch (error) {
      results.push({ event: subject.event, mode, calls, updates, status: "FAILED", error: String(error) });
    } finally { clearTimeout(timer); }
  }
}
const failures = results.filter(result => result.status === "FAILED");
console.log(JSON.stringify({ results, failures, exercised: results.filter(result => result.calls > 0).length,
  not_exercised: results.filter(result => result.status === "NOT_EXERCISED").length }));
process.exitCode = failures.length ? 1 : 0;
"""


def read_failure_instructions():
    """Clarify expected lookup faults without hiding unexpected programming errors."""
    return """Read-only page-load API failures are handled UI outcomes, not uncaught exceptions.
Handle non-success HTTP statuses including an unexpected 503 and rejected API promises.
For session lookup, clear authenticated identity before awaiting, and keep it cleared
after failure; follow the designed error/signed-out state without leaving stale identity.
Catch expected transport/read failures inside the handler, update the declared error or
identity state and return. Do not rethrow after clearing state: the runtime reports that
as a pageerror. Do not disable runtime reporting, change API contracts, hide programming
errors, inspect test globals or fabricate successful responses to pass this check.
"""


def read_failure_subjects(output, interactions, backend, active):
    """Select implemented mount handlers whose declared API effects are read-only GETs."""
    subjects = []
    for eid in sorted(active):
        event = interactions["events"][eid]
        called = api_ids(event)
        if not called or any(
            backend["apis"][aid]["write"]
            or backend["apis"][aid]["signature"]["method"] != "GET"
            for aid in called
        ):
            continue
        entry = implementation_entrypoint(output, "event", eid)
        if not entry:
            continue
        for tid, trigger in interactions["triggers"].items():
            if trigger["action"] != eid or trigger["event"] != "mount":
                continue
            subjects.append(
                {
                    "event": eid,
                    "path": str((output / entry["path"]).resolve()),
                    "export": entry["export"],
                    "trigger": {"id": tid, **trigger},
                }
            )
    return subjects


def check_read_failures(output, ui, interactions, backend, active):
    """Use isolated handler contexts; browser tests still prove UI and persistence behavior."""
    subjects = read_failure_subjects(output, interactions, backend, active)
    if not subjects:
        return {"returncode": 0, "status": "NO_IMPLEMENTED_READ_MOUNTS"}
    config = {
        "subjects": subjects,
        "defaults": {key: record["initial"] for key, record in ui["bindings"].items()},
    }
    with TemporaryDirectory(prefix="arc-read-fault-") as folder:
        root = Path(folder)
        (root / "runner.mjs").write_text(RUNNER)
        (root / "input.json").write_text(json.dumps(config))
        result = capture_process(
            [
                "node",
                "--import",
                "tsx",
                str(root / "runner.mjs"),
                str(root / "input.json"),
            ],
            cwd=output,
            timeout=max(15, len(subjects) * 8),
            timing_kind="read_failure_probe",
        )
    try:
        report = json.loads(result["stdout"])
    except ValueError as error:
        raise ValueError(
            "Read-only failure probe could not load generated handlers: "
            + result["output"]
        ) from error
    return {"returncode": result["returncode"], **report}
