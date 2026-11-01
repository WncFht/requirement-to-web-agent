"""Replay archived label/lookup failures without modifying archived applications."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tarfile
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from infrastructure.stages.frontend.interactions.read_failures import (
    check_read_failures,
)
from infrastructure.utils.processes import capture_process

LABEL_PROBE = r"""import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
const input = JSON.parse(readFileSync(process.argv[2], "utf8"));
const require = createRequire(input.dependencies + "/package.json");
const { chromium, expect } = require("@playwright/test");
const { createElement } = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const { Page } = await import(pathToFileURL(input.page).href);
const html = renderToStaticMarkup(createElement(Page, { data: input.defaults }));
const browser = await chromium.launch();
try {
  const page = await browser.newPage();
  await page.setContent(html, { waitUntil: "domcontentloaded" });
  const results = [];
  for (const control of input.controls) {
    const actual = page.getByTestId(control.id);
    await expect(actual).toHaveAttribute("type", "password");
    await expect(actual).toHaveAccessibleName(control.label);
    const before = await page.getByLabel(control.label, { exact: true }).count();
    let rejected = false;
    try { await expect(page.getByLabel(control.label, { exact: true })).toHaveAttribute("data-testid", control.id, { timeout: 250 }); }
    catch { rejected = true; }
    // Isolated DOM positive control only; neither archive nor saved source is changed.
    await actual.evaluate((element, label) => element.setAttribute("aria-label", label), control.label);
    await expect(page.getByLabel(control.label, { exact: true })).toHaveAttribute("data-testid", control.id);
    results.push({ label: control.label, original_accessible_name_passed: true, exact_count_before: before,
      added_gate_rejected: rejected, positive_control_exact_count: await page.getByLabel(control.label, { exact: true }).count() });
  }
  console.log(JSON.stringify({ scope: "Archived real page rendered statically; DOM-only positive control, not application repair", results }));
} finally { await browser.close(); }
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--dependency-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Refusing to overwrite replay evidence")
    dependencies = args.dependency_root.resolve()
    with TemporaryDirectory(prefix="teacher-contract-replay-") as folder:
        output = Path(folder)
        with tarfile.open(args.archive, "r:gz") as archive:
            prefixes = {Path(member.name).parts[0] for member in archive.getmembers()}
            if len(prefixes) != 1:
                raise ValueError("Expected one archived run")
            prefix = prefixes.pop()
            for member in archive.getmembers():
                relative = Path(*Path(member.name).parts[1:])
                if (
                    not member.isfile()
                    or relative.is_absolute()
                    or ".." in relative.parts
                ):
                    continue
                if (
                    relative.parts[:2] == ("frontend", "src")
                    or relative.parts[:1] == (".arc",)
                    or relative.as_posix()
                    in {
                        "package.json",
                        "frontend/tsconfig.json",
                        "frontend/package.json",
                    }
                ):
                    path = output / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(archive.extractfile(member).read())
        (output / "node_modules").symlink_to(
            dependencies / "node_modules", target_is_directory=True
        )
        read = lambda name: json.loads((output / ".arc" / name).read_text())
        ui, interactions, backend = (
            read("ui_design.json"),
            read("ui_interactions.json"),
            read("backend_contracts.json"),
        )
        fault_result = check_read_failures(
            output, ui, interactions, backend, interactions["events"]
        )
        paths = read("implementation_paths.json")
        controls = [
            {"id": uid, "label": node["prop"]["label"]}
            for uid, node in ui["elements"].items()
            if node.get("prop", {}).get("input_type") == "password"
            and node["prop"]["label"] in {"Password", "Confirm Password"}
            and "register" in uid.lower()
        ]
        config = {
            "dependencies": str(dependencies),
            "page": str(output / paths["page"]["registration"]),
            "defaults": {
                key: record["initial"] for key, record in ui["bindings"].items()
            },
            "controls": controls,
        }
        (output / "label-probe.mjs").write_text(LABEL_PROBE)
        (output / "labels.json").write_text(json.dumps(config))
        label_result = capture_process(
            [
                "node",
                "--import",
                "tsx",
                str(output / "label-probe.mjs"),
                str(output / "labels.json"),
            ],
            cwd=output,
            timeout=30,
            env={
                **os.environ,
                "TSX_TSCONFIG_PATH": str(output / "frontend/tsconfig.json"),
            },
        )
        if label_result["returncode"]:
            raise ValueError(label_result["output"])
        report = {
            "archive_sha256": hashlib.sha256(args.archive.read_bytes()).hexdigest(),
            "labels": json.loads(label_result["stdout"]),
            "read_failures": fault_result,
        }
        if (
            fault_result["returncode"] == 0
            or not controls
            or not all(
                row["added_gate_rejected"] for row in report["labels"]["results"]
            )
        ):
            raise ValueError(
                "Expected archived label and read-handler failures were not reproduced"
            )
        args.output.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
