import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../", import.meta.url));
const entry = fileURLToPath(new URL("../verification/ui.mjs", import.meta.url));
if (!existsSync(entry)) {
  console.error("Create verification/ui.mjs with requirement-derived browser assertions before submitting.");
  process.exit(1);
}

for (const [command, args] of [["npm", ["run", "build"]], [process.execPath, [entry]]]) {
  const result = spawnSync(command, args, { cwd: root, stdio: "inherit" });
  if (result.error) throw result.error;
  if (result.status !== 0) process.exit(result.status ?? 1);
}
