// requirement: REQ-7.1
import { test, expect } from '@playwright/test';
import { home, action, region, login, account } from './helpers';

test("REQ-7.1: Inspect account overview", async ({ page }) => {
  await home(page); await login(page, 'user'); await account(page); await expect(page.getByRole('heading', { name: 'My account', exact: true })).toBeVisible();
  await expect(region(page, 'Account overview')).toContainText('Store User'); for (const name of ['Addresses']) await expect(action(region(page, 'Account overview'), name)).toBeVisible();
});
