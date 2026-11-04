"""Run unchanged generated API assertions through actual Express HTTP wiring."""

import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory


def http_bindings(apis):
    """Adapt the existing test import seam; actual routes and assertions stay unchanged."""
    lines = ['import type Database from "better-sqlite3";',
        'import type { ApiRequest, ApiResponse } from "../../src/api/types.js";',
        'import { createApp } from "../../src/app.js";',
        'import { once } from "node:events";',
        '''async function transport(method: string, route: string, request: ApiRequest, connection: Database.Database): Promise<ApiResponse> {
  let path = route.replace(/:([A-Za-z_][A-Za-z0-9_]*)/g, (_, key: string) => encodeURIComponent(request.params[key] ?? ""));
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(request.query)) {
    if (Array.isArray(value)) for (const item of value) query.append(key, String(item));
    else if (value !== undefined) query.set(key, String(value));
  }
  if (query.size) path += "?" + query;
  const server = createApp(connection).listen(0, "127.0.0.1");
  try {
    await once(server, "listening");
    const address = server.address();
    if (!address || typeof address === "string") throw new Error("No HTTP server address");
    const headers: Record<string, string> = { "content-type": "application/json" };
    for (const [key, value] of Object.entries(request.headers)) if (value !== undefined) headers[key] = value;
    const response = await fetch(`http://127.0.0.1:${address.port}${path}`, {
      method, headers, redirect: "manual", signal: AbortSignal.timeout(10000),
      ...(["GET", "HEAD"].includes(method) ? {} : { body: JSON.stringify(request.body) }),
    });
    const resultHeaders: Record<string, string | string[]> = Object.fromEntries(response.headers.entries());
    const cookies = response.headers.getSetCookie();
    if (cookies.length) resultHeaders["set-cookie"] = cookies.length === 1 ? cookies[0] : cookies;
    return { status: response.status, body: await response.json(), headers: resultHeaders };
  } finally {
    server.closeAllConnections();
    await new Promise<void>((resolve, reject) => server.close(error => error ? reject(error) : resolve()));
  }
}''']
    for api in apis.values():
        signature = api["signature"]
        name = signature["name"]
        # Names already consumed as TypeScript exports by the pinned backend compiler.
        lines.extend([f'export async function {name}(request: ApiRequest, connection: Database.Database): Promise<ApiResponse> {{',
            f'  return transport({json.dumps(signature["method"])}, {json.dumps(signature["path"])}, request, connection);', '}'])
    return "\n".join(lines) + "\n"


def check_http(output, files, apis):
    """Keep original application/tests untouched; use a disposable transport mirror."""
    from infrastructure.stages.backend.testing import BackendChecks
    from infrastructure.shared.agent.frozen_tests import verify_frozen_tests
    verify_frozen_tests(output)
    with TemporaryDirectory(prefix="compiler-http-") as temporary:
        mirror = Path(temporary)
        shutil.copytree(output / "backend", mirror / "backend",
            ignore=shutil.ignore_patterns("node_modules", "dist", "*.db", "*.db-shm", "*.db-wal"))
        shutil.copy2(output / "package.json", mirror / "package.json")
        (mirror / "node_modules").symlink_to((output / "node_modules").resolve(), target_is_directory=True)
        (mirror / "backend/tests/support/apis.ts").write_text(http_bindings(apis))
        checks = BackendChecks(mirror)
        compiled = checks.typecheck(files)
        if compiled["returncode"]:
            return {"returncode": compiled["returncode"], "output": compiled["output"], "tests": 0, "fail": 0}
        result = checks.tests(files)
    verify_frozen_tests(output)
    return {**result, "transport": "real Express HTTP; same API assertions and SQLite connection"}
