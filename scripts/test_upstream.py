"""Run the original upstream unit tests in their own interpreter with no real credentials."""

import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]

GUARD = """import socket
_original_connect = socket.socket.connect
_original_connect_ex = socket.socket.connect_ex

def checked(original):
    def connect(self, address):
        if isinstance(address, tuple) and address[0] not in {"127.0.0.1", "::1", "localhost"}:
            raise RuntimeError("External networking is forbidden in upstream unit tests")
        return original(self, address)
    return connect
socket.socket.connect = checked(_original_connect)
socket.socket.connect_ex = checked(_original_connect_ex)
"""


def run():
    with TemporaryDirectory(prefix="upstream-offline-tests-") as temporary:
        directory = Path(temporary)
        (directory / "sitecustomize.py").write_text(GUARD)
        env = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith(("OPENAI_", "VISUAL_", "ARC_"))
            and key not in {"MODEL", "PYTHONPATH"}
        }
        env.update(PYTHONPATH=str(directory), PYTHON_DOTENV_DISABLED="1", TERM="xterm")
        return subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"],
            cwd=ROOT / "upstream",
            env=env,
            check=False,
        ).returncode


if __name__ == "__main__":
    raise SystemExit(run())
