import os
import platform
import signal
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from minisweagent.exceptions import Submitted
from minisweagent.utils.serialize import recursive_merge


class LocalEnvironmentConfig(BaseModel):
    cwd: str = ""
    env: dict[str, str] = {}
    timeout: int = 30
    output_limit: int = Field(default=20000, ge=1)


class LocalEnvironment:
    def __init__(self, *, config_class: type = LocalEnvironmentConfig, **kwargs):
        """This class executes bash commands directly on the local machine."""
        self.config = config_class(**kwargs)

    def execute(self, action: dict, cwd: str = "", *, timeout: int | None = None) -> dict[str, Any]:
        """Execute a command in the local environment and return the result as a dict."""
        command = action.get("command", "")
        cwd = cwd or self.config.cwd or os.getcwd()
        try:
            output = _run(command, cwd, os.environ | self.config.env,
                          self.config.timeout if timeout is None else timeout, self.config.output_limit)
        except Exception as e:
            raw_output = getattr(e, "output", None)
            raw_output = (
                raw_output.decode("utf-8", errors="replace") if isinstance(raw_output, bytes) else (raw_output or "")
            )
            output = {
                "output": raw_output,
                "returncode": -1,
                "exception_info": f"An error occurred while executing the command: {e}",
                "extra": {"exception_type": type(e).__name__, "exception": str(e)},
            }
        self._check_finished(output)
        return output

    def _check_finished(self, output: dict):
        """Raises Submitted if the output indicates task completion."""
        lines = output.get("output", "").lstrip().splitlines(keepends=True)
        if lines and lines[0].strip() == "COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT" and output["returncode"] == 0:
            submission = "".join(lines[1:])
            raise Submitted(
                {
                    "role": "exit",
                    "content": submission,
                    "extra": {"exit_status": "Submitted", "submission": submission},
                }
            )

    def get_template_vars(self, **kwargs) -> dict[str, Any]:
        return recursive_merge(self.config.model_dump(), platform.uname()._asdict(), os.environ, kwargs)

    def serialize(self) -> dict:
        return {
            "info": {
                "config": {
                    "environment": self.config.model_dump(mode="json"),
                    "environment_type": f"{self.__class__.__module__}.{self.__class__.__name__}",
                }
            }
        }


def _stop(process: subprocess.Popen) -> None:
    """Kill only the foreground command's group and reap the direct child."""
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
    except ProcessLookupError:
        pass
    process.wait(timeout=1)


def _run(command: str, cwd: str, env: dict[str, str], timeout: float, output_limit: int) -> dict[str, Any]:
    """Wait for the shell itself, independently of inherited output handles.

    Normal completion preserves explicitly backgrounded services. They must
    detach and redirect their own logs; this executor is not a service registry.
    """
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    log_dir = Path(cwd).resolve() / ".agent" / "commands"
    log_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix="bash-", suffix=".log", dir=log_dir, delete=False) as log:
        process = subprocess.Popen(
            ["bash", "--noprofile", "--norc", "-o", "pipefail", "-c", command],
            cwd=cwd,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=os.name == "posix",
        )
        timed_out = False
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            _stop(process)
        finally:
            if process.poll() is None:
                _stop(process)
        # Use a separate read cursor: descendants can still hold the writer.
        # Capture a bounded snapshot rather than waiting for EOF or reading all output.
        with open(log.name, "rb") as stream:
            size = os.fstat(stream.fileno()).st_size
            stream.seek(max(0, size - output_limit))
            text = stream.read(min(size, output_limit)).decode("utf-8", errors="replace")
        output = {
            "output": text,
            "returncode": -1 if timed_out else process.returncode,
            "exception_info": f"Command timed out after {timeout} seconds" if timed_out else "",
            "log_path": log.name,
            "output_bytes": size,
            "output_truncated": size > output_limit,
        }
        if timed_out:
            output["extra"] = {"exception_type": "TimeoutExpired", "exception": output["exception_info"]}
        return output
