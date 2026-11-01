// Reproduce the archived OPT-F artifact's cross-API failure in an in-memory DB.
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

const root = resolve(process.argv[2] ?? ".");
const load = path => import(pathToFileURL(resolve(root, path)).href);
const { createDatabaseClient } = await load("backend/src/db/client.ts");
const { initializeDatabase } = await load("backend/src/db/initialize.ts");
const { handle: register } = await load("backend/src/create-account.ts");
const { handle: session } = await load("backend/src/get-current-session-user.ts");
const db = createDatabaseClient(":memory:");
try {
  initializeDatabase(db);
  const body = {
    username: "probe_user", password: "ProbePass123!", confirmPassword: "ProbePass123!",
    email: "probe@example.test", nationality: "Vietnam", name: "Probe User",
    passportNumber: "P1234567", passportExpirationDate: "2030-01-01",
    dateOfBirth: "1990-01-01", gender: "Male", agreementConsent: true,
  };
  const created = await register({ body, headers: {}, params: {}, query: {} }, db);
  const cookie = created.headers["set-cookie"].split(";")[0];
  const token = cookie.slice(cookie.indexOf("=") + 1);
  const persisted = db.prepare("SELECT credential FROM Session").get().credential;
  const current = await session({ headers: { cookie }, params: {}, query: {}, body: {} }, db);
  console.log(JSON.stringify({
    registration_status: created.status,
    cookie_matches_persisted_credential: token === persisted,
    session_status: current.status,
    authenticated: current.body.authenticated,
  }, null, 2));
} finally {
  db.close();
}
