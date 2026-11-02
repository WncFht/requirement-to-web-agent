"""Timeout cleanup must reach owned detached descendants and preserve unrelated services."""

import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
import unittest
from unittest.mock import patch

from infrastructure.utils.processes import (
    capture_process,
    start_process,
    stop_process,
    owned_descendants,
)


@unittest.skipIf(
    os.name == "nt",
    "POSIX detached-group regression; Windows taskkill has separate tests",
)
class DetachedCleanupTests(unittest.TestCase):
    def test_detached_owned_service_stops_and_unrelated_service_survives(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            heartbeat = "import pathlib,time,sys; p=pathlib.Path(sys.argv[1]);\nwhile True:\n p.open('a').write('x');time.sleep(.03)"
            parent = "import subprocess,sys,time;subprocess.Popen([sys.executable,'-c',sys.argv[1],'owned'],start_new_session=True);time.sleep(60)"
            sibling = start_process(
                [sys.executable, "-c", heartbeat, "unrelated"], cwd=root
            )
            try:
                with self.assertRaises(subprocess.TimeoutExpired):
                    capture_process(
                        [sys.executable, "-c", parent, heartbeat],
                        cwd=root,
                        timeout=1,
                    )
                owned = (root / "owned").read_bytes()
                unrelated = (root / "unrelated").read_bytes()
                time.sleep(0.2)
                self.assertEqual((root / "owned").read_bytes(), owned)
                self.assertGreater(
                    len((root / "unrelated").read_bytes()), len(unrelated)
                )
                self.assertIsNone(sibling.poll())
            finally:
                stop_process(sibling)

    def test_snapshot_only_walks_owned_descendants(self):
        result = subprocess.CompletedProcess(
            [], 0, stdout="10 1\n11 10\n12 11\n99 1\n100 99\n"
        )
        with patch(
            "infrastructure.utils.processes.subprocess.run", return_value=result
        ):
            self.assertEqual(set(owned_descendants(10)), {11, 12})
