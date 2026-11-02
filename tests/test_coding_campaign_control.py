"""Stopping an experiment must also stop its real owned child process."""

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
import unittest
from unittest.mock import patch

from scripts.run_coding_campaign import prepare_environment


class CodingCampaignControlTests(unittest.TestCase):
    def test_evaluation_uses_the_same_node_path_as_the_generation_environment(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            node_bin = root / "node-bin"
            node_bin.mkdir()
            node = node_bin / "node"
            node.write_text("#!/bin/sh\nexit 0\n")
            node.chmod(0o755)
            (root / ".env").write_text(
                "OPENAI_BASE_URL=http://unused.invalid/v1\nOPENAI_API_KEY=local-fixture\n"
            )
            with patch.dict(os.environ, {"PATH": "/usr/bin"}, clear=True):
                env = prepare_environment(root, node_bin)
                self.assertEqual(os.environ["PATH"], env["PATH"])
                self.assertEqual(Path(env["PATH"].split(os.pathsep)[0]), node_bin)
                self.assertNotIn("OPENAI_API_KEY", os.environ)
                with self.assertRaisesRegex(ValueError, "directory containing"):
                    prepare_environment(root / ".env", node_bin)

    @unittest.skipIf(os.name == "nt", "POSIX SIGTERM process ownership regression")
    def test_sigterm_produces_interrupted_result_and_waits_for_owned_child(self):
        driver_code = """import json,os,sys
from pathlib import Path
from scripts.run_coding_campaign import command_phase,install_signal_handlers
install_signal_handlers()
result=command_phase([sys.executable,'-c','import os,time\\nprint(os.getpid(),flush=True)\\ntime.sleep(60)'],Path.cwd(),dict(os.environ),Path(sys.argv[1]),120)
print(json.dumps(result),flush=True)
"""
        with TemporaryDirectory() as tmp:
            log = Path(tmp) / "child.log"
            driver = subprocess.Popen(
                [sys.executable, "-c", driver_code, str(log)],
                cwd=Path(__file__).resolve().parents[1],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                start_new_session=True,
            )
            try:
                deadline = time.monotonic() + 10
                while not log.exists() or not log.read_text().strip():
                    if driver.poll() is not None or time.monotonic() > deadline:
                        self.fail("Fixture child did not start")
                    time.sleep(0.05)
                child_pid = int(log.read_text().strip())
                driver.send_signal(signal.SIGTERM)
                stdout, stderr = driver.communicate(timeout=10)
                self.assertEqual(driver.returncode, 0, stderr)
                self.assertEqual(json.loads(stdout)["status"], "interrupted")
                with self.assertRaises(ProcessLookupError):
                    os.kill(child_pid, 0)
            finally:
                if driver.poll() is None:
                    driver.kill()
                driver.communicate(timeout=5)
