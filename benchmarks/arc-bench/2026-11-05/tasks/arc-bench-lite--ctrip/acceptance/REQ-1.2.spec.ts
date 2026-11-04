// requirement: REQ-1.2
import { test } from "@playwright/test";
import { field, visible, heading, openHome, installClock, openLogin } from "./helpers";

test.beforeEach(async ({ page }) => { await installClock(page); });

test('REQ-1.2: Open password login', async ({ page }, testInfo) => {
  await openHome(page);
  await openLogin(page);
  await heading(page, 'Log in');
  await visible(field(page, 'Account'));
  await visible(field(page, 'Password'));
});

