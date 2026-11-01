// Independent fixed acceptance fixtures; no generated assertion or UI fixture is used.
import { test as base, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
import { createDatabaseClient } from "../../../backend/src/db/client.js";
import { initializeDatabase } from "../../../backend/src/db/initialize.js";
import { fixturePasswordHash } from "../../../backend/tests/support/context.js";

export const adapter = JSON.parse(readFileSync(new URL("./adapter.json", import.meta.url), "utf8"));
export const quote = (name: string) => `"${name.replaceAll('"', '""')}"`;
export function database() {
  const filename = process.env.ARC_E2E_DB_FILE;
  if (!filename || !filename.includes("teacher-acceptance-")) throw new Error("Use the independent acceptance runner");
  return createDatabaseClient(filename);
}
export function reset() {
  const db = database();
  try {
    initializeDatabase(db);
    db.pragma("foreign_keys = OFF");
    db.transaction(() => {
      for (const row of db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").all() as { name: string }[]) {
        db.exec(`DELETE FROM ${quote(row.name)}`);
      }
      const account = { ...adapter.account_seed, [adapter.account_fields.password_hash]: fixturePasswordHash("TakenSmoke!2026") };
      db.prepare(`INSERT INTO ${quote(adapter.account_table)} (${Object.keys(account).map(quote).join(",")}) VALUES (${Object.keys(account).map(() => "?").join(",")})`).run(...Object.values(account));
      const session = adapter.session_seed;
      db.prepare(`INSERT INTO ${quote(adapter.session_table)} (${Object.keys(session).map(quote).join(",")}) VALUES (${Object.keys(session).map(() => "?").join(",")})`).run(...Object.values(session));
    })();
    db.pragma("foreign_keys = ON");
    if (db.pragma("foreign_key_check").length) throw new Error("Acceptance seed violates foreign keys");
  } finally { db.close(); }
}
export function rows(table: string): Record<string, unknown>[] {
  const db = database();
  try { return db.prepare(`SELECT * FROM ${quote(table)}`).all() as Record<string, unknown>[]; }
  finally { db.close(); }
}
export function snapshot() {
  const db = database();
  try {
    const names = (db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").all() as { name: string }[]).map(row => row.name);
    return Object.fromEntries(names.map(name => [name, db.prepare(`SELECT * FROM ${quote(name)}`).all().map(row => JSON.stringify(row)).sort()]));
  } finally { db.close(); }
}
export const test = base.extend<{ fixedState: void }>({
  fixedState: [async ({ page }, use) => {
    reset();
    const errors: string[] = [];
    page.on("pageerror", error => errors.push(error.message));
    try { await use(); expect(errors).toEqual([]); }
    finally { reset(); }
  }, { auto: true }],
});
export { expect };
