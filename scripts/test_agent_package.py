"""Exercise the actual extracted upload ZIP through a local, zero-fee compatible API."""

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from threading import Thread
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
from coding_fixture import FixtureModel
from coding_agent.trace import json_write, audit
from coding_agent.checks import application_environment


def verify(package, directory, dependencies):
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=False)
    source = directory / "source"
    with zipfile.ZipFile(package) as archive:
        archive.extractall(source)
    inputs = directory / "input"
    inputs.mkdir()
    (inputs / "requirements.yaml").write_text("id: REQ-1\nname: Notes\nchildren: []\n")
    output = directory / "output"
    output.mkdir()
    shutil.copytree(dependencies, output / "node_modules", symlinks=True)
    fixture = FixtureModel(type("Config", (), {"output": output})(), None)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            json.loads(self.rfile.read(int(self.headers["content-length"])))
            action = fixture.next_action()
            body = {
                "id": f"local-{fixture.index}",
                "object": "chat.completion",
                "created": 0,
                "model": "local-fixture",
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "stop",
                        "message": {"role": "assistant", "content": json.dumps(action)},
                    }
                ],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 3,
                    "total_tokens": 13,
                },
            }
            data = json.dumps(body).encode()
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    env = application_environment() | {
        "OPENAI_BASE_URL": f"http://127.0.0.1:{server.server_port}/v1",
        "OPENAI_API_KEY": "local-fixture-token",
        "ARC_AGENT_MAX_SECONDS": "180",
        "ARC_AGENT_MAX_TURNS": "8",
    }
    env.pop("ARC_AGENT_ENGINE", None)
    try:
        with (directory / "generation.log").open("w") as log:
            generated = subprocess.run(
                [
                    sys.executable,
                    "main.py",
                    str(inputs),
                    "--output-dir",
                    str(output),
                    "--port",
                    "34567",
                ],
                cwd=source,
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
                timeout=210,
                check=False,
            )
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    proof = audit(output)
    result = {
        "returncode": generated.returncode,
        "audit_valid": proof["valid"],
        "issues": proof["issues"],
        "status": proof["result"]["status"],
        "model_calls": proof["result"]["model_calls"],
        "no_env_in_package": not (source / ".env").exists(),
        "default_engine": json.loads((source / "engine.json").read_text())["default"],
        "credentials": "local mock only, no paid requests",
    }
    json_write(directory / "result.json", result)
    if (
        generated.returncode
        or not proof["valid"]
        or result["status"] != "INTERNAL_GREEN"
    ):
        raise ValueError(json.dumps(result))
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("package", type=Path)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--dependencies", type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(verify(a.package, a.output, a.dependencies), indent=2))
