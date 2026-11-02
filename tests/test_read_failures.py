"""Execute the fault runner against bad, handled and non-exercised real JS handlers."""

import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

from infrastructure.stages.frontend.interactions.read_failures import (
    RUNNER,
    read_failure_subjects,
)
from infrastructure.utils.processes import capture_process
from infrastructure.utils.files import save_json, save_text


class ReadFailureTests(unittest.TestCase):
    def execute(self, source):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            save_text(root / "handler.mjs", source)
            save_text(root / "runner.mjs", RUNNER)
            save_json(
                root / "input.json",
                {
                    "defaults": {"authenticated": True},
                    "subjects": [
                        {
                            "event": "load",
                            "path": str(root / "handler.mjs"),
                            "export": "handle",
                            "trigger": {"event": "mount"},
                        }
                    ],
                },
            )
            result = capture_process(
                [
                    shutil.which("node") or "node",
                    str(root / "runner.mjs"),
                    str(root / "input.json"),
                ],
                cwd=root,
                timeout=10,
            )
            return result["returncode"], json.loads(result["stdout"])

    def test_unhandled_http_and_transport_failures_are_rejected(self):
        code, report = self.execute(
            'export async function handle(c) { const r = await c.api("read"); if (r.status !== 200) throw new Error("Unexpected session response status: " + r.status); }'
        )
        self.assertEqual(code, 1)
        self.assertEqual(len(report["failures"]), 2)
        self.assertIn("503", report["failures"][0]["error"])
        self.assertIn("transport failure", report["failures"][1]["error"])

    def test_handled_failure_passes_and_programming_errors_still_fail(self):
        code, report = self.execute(
            'export async function handle(c) { try { const r = await c.api("read"); if (r.status !== 200) c.update({authenticated:false}); } catch { c.update({authenticated:false}); } }'
        )
        self.assertEqual(code, 0)
        self.assertEqual(report["exercised"], 2)
        self.assertTrue(all(row["updates"] == 1 for row in report["results"]))
        code, report = self.execute(
            'export async function handle() { throw new TypeError("real programming bug"); }'
        )
        self.assertEqual(code, 1)
        self.assertEqual(len(report["failures"]), 2)

    def test_unreached_api_is_reported_without_claiming_exercise(self):
        code, report = self.execute("export function handle() {}")
        self.assertEqual(code, 0)
        self.assertEqual(report["exercised"], 0)
        self.assertEqual(report["not_exercised"], 2)
        self.assertTrue(
            all(row["status"] == "NOT_EXERCISED" for row in report["results"])
        )

    def test_selects_only_implemented_read_only_mount_handlers(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            save_text(root / "frontend/src/load.ts", "export function handle() {}")
            save_json(
                root / ".arc/implementation_paths.json",
                {
                    "event": {
                        "load": "frontend/src/load.ts",
                        "write": "frontend/src/load.ts",
                        "click": "frontend/src/load.ts",
                    }
                },
            )
            backend = {
                "apis": {
                    "read": {"write": [], "signature": {"method": "GET"}},
                    "write": {"write": ["Account.id"], "signature": {"method": "POST"}},
                }
            }
            interactions = {
                "events": {
                    key: {
                        "actions": [
                            {
                                "kind": "api",
                                "api": "write" if key == "write" else "read",
                            }
                        ]
                    }
                    for key in ["load", "missing", "write", "click"]
                },
                "triggers": {
                    key: {
                        "action": key,
                        "source": "root",
                        "event": "click" if key == "click" else "mount",
                    }
                    for key in ["load", "missing", "write", "click"]
                },
            }
            subjects = read_failure_subjects(
                root, interactions, backend, interactions["events"]
            )
            self.assertEqual([s["event"] for s in subjects], ["load"])
