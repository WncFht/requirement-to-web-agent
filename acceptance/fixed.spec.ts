import { test, expect, adapter, rows, snapshot } from "./context";
import {
  AGREEMENT, EXISTING_ACCOUNT, button, entry, expectSignedIn, expectSignedOut,
  fillRegistration, newAccount, openRegistration, passwordField, registerAccount, signIn,
} from "./teacher/helpers";

// Assertions are fixed in source; adapter only identifies generated storage and routes.
test("F01: signed-out home and navigation never mutate records", async ({ page }) => {
  const before = snapshot();
  await entry(page);
  await expectSignedOut(page);
  await expect(page.getByRole("link", { name: "Register", exact: true })).toHaveAttribute("href", "/register");
  await expect(page.getByRole("link", { name: "Login", exact: true })).toHaveAttribute("href", "/login");
  await expect(page.getByText(EXISTING_ACCOUNT.username, { exact: true })).toHaveCount(0);
  await openRegistration(page);
  await page.goto("/");
  await page.getByRole("link", { name: "Login", exact: true }).click();
  await expect(page).toHaveURL(/\/login\/?$/);
  expect(snapshot()).toEqual(before);
});

test("F02: seeded existing session restores exact identity read-only after refresh", async ({ page, context, baseURL }) => {
  const before = snapshot();
  await context.addCookies([{ name: adapter.cookie_name, value: adapter.session_token, url: baseURL! }]);
  await entry(page);
  await expectSignedIn(page, EXISTING_ACCOUNT);
  await page.reload();
  await expectSignedIn(page, EXISTING_ACCOUNT);
  expect(snapshot()).toEqual(before);
  await expect(page.locator("body")).not.toContainText(adapter.session_token);
  await expect(page.locator("body")).not.toContainText("scrypt$");
});

test("F03: unknown session is signed out and leaves every record unchanged", async ({ page, context, baseURL }) => {
  const before = snapshot();
  await context.addCookies([{ name: adapter.cookie_name, value: "fixed-unknown-session", url: baseURL! }]);
  await entry(page);
  await expectSignedOut(page);
  await expect(page.getByText(EXISTING_ACCOUNT.username, { exact: true })).toHaveCount(0);
  await page.reload();
  await expectSignedOut(page);
  expect(snapshot()).toEqual(before);
});

test("F04: real pending and failed session lookup do not expose cached identity", async ({ page, context, baseURL }) => {
  await context.addCookies([{ name: adapter.cookie_name, value: adapter.session_token, url: baseURL! }]);
  await entry(page);
  await expectSignedIn(page, EXISTING_ACCOUNT);
  const before = snapshot();
  let release!: () => void;
  const held = new Promise<void>(resolve => { release = resolve; });
  let reached!: () => void;
  const started = new Promise<void>(resolve => { reached = resolve; });
  const failedResponse = page.waitForResponse(response =>
    new URL(response.url()).pathname === adapter.session_path && response.status() === 503);
  await page.route(`**${adapter.session_path}`, async route => {
    reached(); await held; await route.fulfill({ status: 503, contentType: "application/json", body: '{"error":"fixed lookup failure"}' });
  });
  try {
    await page.reload({ waitUntil: "domcontentloaded" });
    await started;
    await expect(page.getByText(EXISTING_ACCOUNT.username, { exact: true })).toHaveCount(0);
  } finally { release(); }
  expect((await failedResponse).status()).toBe(503);
  await page.waitForLoadState("networkidle");
  await expect(page.getByText(EXISTING_ACCOUNT.username, { exact: true })).toHaveCount(0);
  expect(snapshot()).toEqual(before);
});

test("F05: registration stores required data and a usable hash/session", async ({ page }) => {
  const account = newAccount();
  const beforeAccounts = rows(adapter.account_table);
  const beforeSessions = rows(adapter.session_table);
  await entry(page);
  await registerAccount(page, account);
  await page.reload();
  await expectSignedIn(page, account);
  const accounts = rows(adapter.account_table);
  const sessions = rows(adapter.session_table);
  expect(accounts).toHaveLength(beforeAccounts.length + 1);
  expect(sessions).toHaveLength(beforeSessions.length + 1);
  const field = adapter.account_fields;
  const created = accounts.find(row => row[field.username] === account.username)!;
  expect(created).toBeTruthy();
  for (const [role, value] of Object.entries({ nationality: "Vietnam", name: account.name, passport_number: account.passport, passport_expiration_date: "2099-12-31", date_of_birth: "1995-06-15", email: account.email })) {
    expect(String(created[field[role]])).toBe(value);
  }
  expect(String(created[field.gender]).toLowerCase()).toBe("male");
  expect([true, 1]).toContain(created[field.agreement_consent]);
  expect(String(created[field.password_hash]).length).toBeGreaterThan(20);
  expect(JSON.stringify(accounts)).not.toContain(account.password);
  expect(Object.keys(created).some(key => /confirm.*password|password.*confirm/i.test(key))).toBe(false);
  await page.context().clearCookies();
  await entry(page);
  await signIn(page, account.username, account.password);
  await expectSignedIn(page, account);
  await page.reload();
  await expectSignedIn(page, account);
  expect(rows(adapter.account_table)).toEqual(accounts);
});

test("F06: duplicate exact username is rejected without any database write", async ({ page }) => {
  const before = snapshot();
  await entry(page); await openRegistration(page);
  await fillRegistration(page, { ...newAccount(), username: EXISTING_ACCOUNT.username });
  await button(page, "Next step").click();
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(page.getByRole("alert")).not.toHaveText("");
  expect(snapshot()).toEqual(before);
  await entry(page); await page.reload(); await expectSignedOut(page);
});

test("F07: username uniqueness uses exact case, not case folding", async ({ page }) => {
  const different = { ...newAccount(), username: "Taken_Traveler" };
  await entry(page); await registerAccount(page, different);
  await page.reload(); await expectSignedIn(page, different);
  const names = rows(adapter.account_table).map(row => row[adapter.account_fields.username]);
  expect(names).toContain("taken_traveler"); expect(names).toContain("Taken_Traveler");
});

test("F08: correct login creates only one session and preserves accounts", async ({ page }) => {
  const accounts = rows(adapter.account_table);
  const sessions = rows(adapter.session_table);
  await entry(page); await signIn(page, EXISTING_ACCOUNT.username, EXISTING_ACCOUNT.password);
  await expectSignedIn(page, EXISTING_ACCOUNT);
  await page.reload(); await expectSignedIn(page, EXISTING_ACCOUNT);
  expect(rows(adapter.account_table)).toEqual(accounts);
  expect(rows(adapter.session_table)).toHaveLength(sessions.length + 1);
});

test("F09: wrong password shows alert and changes no record", async ({ page }) => {
  const before = snapshot();
  await entry(page); await signIn(page, EXISTING_ACCOUNT.username, "WrongSmoke!2026");
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(page.getByRole("alert")).not.toHaveText("");
  expect(snapshot()).toEqual(before);
  await entry(page); await page.reload(); await expectSignedOut(page);
});

test("F10: exact agreement and authentication labels conceal passwords", async ({ page }) => {
  await entry(page); await openRegistration(page);
  await expect(page.getByRole("checkbox", { name: AGREEMENT, exact: true })).toBeVisible();
  await expect(passwordField(page, "Password")).toHaveAttribute("type", "password");
  await expect(passwordField(page, "Confirm Password")).toHaveAttribute("type", "password");
  await expect(button(page, "Next step")).toBeVisible();
  await page.goto("/login");
  await expect(page.getByRole("textbox", { name: "Email/Username/Mobile number", exact: true })).toHaveAttribute("placeholder", "Email/Username/Mobile number");
  await expect(passwordField(page, "Password")).toHaveAttribute("type", "password");
  await expect(button(page, "LOGIN")).toBeVisible();
});
