"""Check historical packaging, committed source isolation, and local runner boundaries."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from package_agent import inspect_package, package
import run_submission


class SubmissionPackageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory(prefix="submission test ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        self.source.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.write(
            "main.py",
            'import os\nprint(os.environ["ARC_AGENT_ENGINE"], os.environ["MODEL"], os.environ["OPENAI_BASE_URL"], os.environ["OPENAI_API_KEY"])\n',
        )
        self.write("run_all.py", "# fixture pipeline\n")
        self.write("requirements.txt", "# fixture dependencies\n")
        self.write("infrastructure/utils/cli.py", "# fixture module\n")
        self.write(
            "infrastructure/shared/project/templates/deploy.sh", "#!/bin/sh\nexit 0\n"
        )
        for number in range(13):
            self.write(f"{number:02d}_stage.py", f"STAGE = {number}\n")
        self.old = self.commit()
        self.git("tag", "old-legacy")
        self.write("coding_agent/loop.py", "# fixture coding engine\n")
        for number in range(13):
            old = self.source / f"{number:02d}_stage.py"
            new = self.source / "legacy" / old.name
            new.parent.mkdir(exist_ok=True)
            old.rename(new)
        self.new = self.commit()

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.source).decode().strip()

    def write(self, name, value):
        path = self.source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")
        return self.git("rev-parse", "HEAD")

    def build(self, engine="legacy", ref="HEAD", name="upload.zip"):
        return package(self.root / name, ref, engine, root=self.source)

    def test_selects_committed_version_without_checkout_or_dirty_files(self):
        self.write("legacy/00_stage.py", "raise RuntimeError('uncommitted')\n")
        self.write("infrastructure/utils/cli.py", "raise RuntimeError('uncommitted')\n")
        self.write(".env", "SECRET=fixture-only\n")
        self.write("input/requirements.yaml", "private fixture\n")
        status = self.git("status", "--porcelain")
        result = self.build(ref="old-legacy")
        self.assertEqual(result["revision"], self.old)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.new)
        self.assertEqual(self.git("status", "--porcelain"), status)
        with zipfile.ZipFile(result["zip_path"]) as archive:
            names = set(archive.namelist())
            self.assertIn("00_stage.py", names)
            self.assertNotIn("legacy/00_stage.py", names)
            self.assertNotIn("coding_agent/loop.py", names)
            self.assertNotIn("input/requirements.yaml", names)
            self.assertNotIn(".env", names)
            self.assertIn("infrastructure/shared/project/templates/deploy.sh", names)
            self.assertEqual(
                archive.read("infrastructure/utils/cli.py"), b"# fixture module\n"
            )
        self.assertEqual(inspect_package(result["zip_path"]), result)

    def test_new_layout_and_engine_have_separate_packages(self):
        legacy = self.build(name="legacy.zip")
        coding = self.build("coding", name="coding.zip")
        with zipfile.ZipFile(legacy["zip_path"]) as archive:
            self.assertIn("legacy/12_stage.py", archive.namelist())
            self.assertNotIn("coding_agent/loop.py", archive.namelist())
        with zipfile.ZipFile(coding["zip_path"]) as archive:
            self.assertIn("coding_agent/loop.py", archive.namelist())
            self.assertNotIn("run_all.py", archive.namelist())
            self.assertNotIn("legacy/12_stage.py", archive.namelist())
        with self.assertRaisesRegex(ValueError, "does not support coding"):
            self.build("coding", ref="old-legacy", name="unsupported.zip")

    def test_entrypoint_fixes_engine_preserves_endpoint_and_supplies_model(self):
        for engine in ("legacy", "coding"):
            with self.subTest(engine=engine):
                result = self.build(engine, name=engine + ".zip")
                destination = self.root / engine
                with zipfile.ZipFile(result["zip_path"]) as archive:
                    archive.extractall(destination)
                environment = {
                    **os.environ,
                    "ARC_AGENT_ENGINE": "opposite",
                    "OPENAI_BASE_URL": "https://fixture.invalid/v1",
                    "OPENAI_API_KEY": "fixture-key",
                }
                environment.pop("MODEL", None)
                command = [sys.executable, str(destination / "main.py")]
                actual = subprocess.check_output(
                    command, env=environment, text=True
                ).strip()
                self.assertEqual(
                    actual,
                    f"{engine} deepseek-flash https://fixture.invalid/v1 fixture-key",
                )
                environment["MODEL"] = "chosen-model"
                self.assertIn(
                    "chosen-model",
                    subprocess.check_output(command, env=environment, text=True),
                )
                self.assertEqual(
                    result["source_files"]["main.py"],
                    hashlib.sha256(
                        (destination / "_agent_main.py").read_bytes()
                    ).hexdigest(),
                )

    def test_deterministic_reuse_and_no_overwrite_or_tampered_manifest(self):
        result = self.build()
        duplicate = self.build(ref=self.new, name="duplicate.zip")
        self.assertEqual(result["zip_sha256"], duplicate["zip_sha256"])
        self.assertEqual(self.build(ref=self.new), result)
        with self.assertRaisesRegex(ValueError, "overwrite"):
            self.build("coding")
        manifest_path = Path(result["zip_path"]).with_suffix(".json")
        modified = dict(result)
        modified["files"] = {}
        manifest_path.write_text(json.dumps(modified))
        with self.assertRaisesRegex(ValueError, "differ from manifest"):
            self.build()

    def test_rejects_linked_runtime_sources_and_incomplete_legacy(self):
        self.git("rm", "legacy/12_stage.py")
        self.commit()
        with self.assertRaisesRegex(ValueError, "stage 12"):
            self.build()
        target = self.source / "infrastructure/link.py"
        try:
            target.symlink_to("utils/cli.py")
        except OSError:
            self.skipTest("Host does not permit symlinks")
        self.commit()
        with self.assertRaisesRegex(ValueError, "Unsupported runtime source"):
            self.build("coding")

    def test_current_upstream_and_coding_packages_are_isolated(self):
        self.write("runtime/output.py", "# platform output adapter\n")
        self.write("runtime/processes.py", "# platform process ownership\n")
        self.write("upstream.json", '{"revision":"pinned-fixture"}')
        self.write("upstream/main.py", "# upstream CLI\n")
        self.write("upstream/infrastructure/compiler.py", "# upstream compiler\n")
        self.write(
            "upstream/infrastructure/shared/project/templates/deploy.sh",
            "#!/bin/sh\nexit 0\n",
        )
        for number in range(13):
            self.write(f"upstream/{number:02d}_stage.py", f"STAGE = {number}\n")
        self.write("upstream/tests/test_compiler.py", "# development only\n")
        self.write("upstream/input/requirements.yaml", "private fixture\n")
        self.write("coding_agent/support/shared/project/templates/package.json", "{}")
        self.commit()
        teacher = self.build("upstream", name="upstream.zip")
        coding = self.build("coding", name="coding-current.zip")
        with zipfile.ZipFile(teacher["zip_path"]) as archive:
            names = archive.namelist()
            self.assertIn("upstream/infrastructure/compiler.py", names)
            self.assertIn("runtime/output.py", names)
            self.assertNotIn("coding_agent/loop.py", names)
            self.assertNotIn("upstream/tests/test_compiler.py", names)
            self.assertNotIn("upstream/input/requirements.yaml", names)
            self.assertNotIn("legacy/00_stage.py", names)
        with zipfile.ZipFile(coding["zip_path"]) as archive:
            names = archive.namelist()
            self.assertIn("coding_agent/loop.py", names)
            self.assertIn(
                "coding_agent/support/shared/project/templates/package.json", names
            )
            self.assertNotIn("upstream/main.py", names)
            self.assertNotIn("infrastructure/utils/cli.py", names)
        with self.assertRaisesRegex(ValueError, "archived"):
            self.build("legacy", name="invalid-current-legacy.zip")

    def test_current_compiler_and_coding_packages_are_isolated(self):
        self.write("runtime/output.py", "# platform output adapter\n")
        self.write("runtime/processes.py", "# platform process ownership\n")
        self.write("compiler.json", '{"revision":"pinned-fixture"}')
        self.write("compiler/main.py", "# compiler CLI\n")
        self.write("compiler/infrastructure/compiler.py", "# compiler compiler\n")
        self.write(
            "compiler/infrastructure/shared/project/templates/deploy.sh",
            "#!/bin/sh\nexit 0\n",
        )
        for number in range(13):
            self.write(f"compiler/{number:02d}_stage.py", f"STAGE = {number}\n")
        self.write("compiler/tests/test_compiler.py", "# development only\n")
        self.write("compiler/input/requirements.yaml", "private fixture\n")
        self.write("coding_agent/support/shared/project/templates/package.json", "{}")
        self.commit()
        teacher = self.build("compiler", name="compiler.zip")
        coding = self.build("coding", name="coding-current.zip")
        with zipfile.ZipFile(teacher["zip_path"]) as archive:
            names = archive.namelist()
            self.assertIn("compiler/infrastructure/compiler.py", names)
            self.assertIn("runtime/output.py", names)
            self.assertNotIn("coding_agent/loop.py", names)
            self.assertNotIn("compiler/tests/test_compiler.py", names)
            self.assertNotIn("compiler/input/requirements.yaml", names)
            self.assertNotIn("legacy/00_stage.py", names)
        with zipfile.ZipFile(coding["zip_path"]) as archive:
            names = archive.namelist()
            self.assertIn("coding_agent/loop.py", names)
            self.assertIn(
                "coding_agent/support/shared/project/templates/package.json", names
            )
            self.assertNotIn("compiler/main.py", names)
            self.assertNotIn("infrastructure/utils/cli.py", names)
        with self.assertRaisesRegex(ValueError, "archived"):
            self.build("legacy", name="invalid-current-legacy.zip")


class SubmissionRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.inputs = self.root / "input"
        self.inputs.mkdir()
        (self.inputs / "requirements.yaml").write_text("children: []\n")
        self.output = self.root / "new output"
        self.environment = {
            "OPENAI_API_KEY": "fixture",
            "OPENAI_BASE_URL": "https://fixture.invalid",
        }

    def prepare(self, output=None):
        return run_submission.prepare(
            self.inputs, str(output or self.output), 3000, self.environment
        )

    def test_rejects_existing_output_missing_credentials_and_wrong_node(self):
        self.output.mkdir()
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.prepare()
        self.output.rmdir()
        self.environment.clear()
        with self.assertRaisesRegex(ValueError, "required"):
            self.prepare()
        self.environment.update(
            OPENAI_API_KEY="fixture", OPENAI_BASE_URL="https://fixture.invalid"
        )
        with patch.object(
            run_submission.subprocess, "check_output", return_value="v24.0.0"
        ):
            with self.assertRaisesRegex(ValueError, "Node 22"):
                self.prepare()

    def test_repository_output_is_confined_to_work(self):
        with (
            patch.object(run_submission, "ROOT", self.root),
            patch.object(
                run_submission.subprocess, "check_output", return_value="v22.23.2"
            ),
        ):
            self.prepare(self.root / "work" / "round-01")
            with self.assertRaisesRegex(ValueError, "gitignored work"):
                self.prepare(self.root / "compiler" / "new-run")
            (self.root / "work").symlink_to(self.root.parent, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "gitignored work"):
                self.prepare(
                    self.root / "work" / self.root.name / "compiler" / "new-run"
                )

    def test_runner_uses_packaged_version_and_leaves_output_empty_for_generator(self):
        archive = self.root / "package.zip"
        with zipfile.ZipFile(archive, "w") as stream:
            stream.writestr("main.py", "# local fixture only\n")
        manifest = {
            "revision": "f" * 40,
            "default_engine": "coding",
            "zip_sha256": "a" * 64,
            "zip_path": str(archive),
        }

        def start(command, *, cwd, env):
            self.assertEqual(list(self.output.iterdir()), [])
            self.assertEqual(command[1], "main.py")
            self.assertEqual(Path(command[4]), self.output)
            self.assertTrue((cwd / "main.py").is_file())
            return type("Child", (), {"wait": lambda _: 7})()

        with (
            patch.object(
                run_submission, "prepare", return_value=(self.inputs, self.output)
            ),
            patch.object(run_submission, "package", return_value=manifest) as build,
            patch.object(run_submission, "start_process", side_effect=start),
        ):
            code = run_submission.run("a-tag", "coding", self.inputs, self.output, 3000)
        self.assertEqual(code, 7)
        build.assert_called_once_with(ref="a-tag", engine="coding")
        record = self.output.with_name(self.output.name + ".run.json")
        self.assertEqual(json.loads(record.read_text())["revision"], "f" * 40)
