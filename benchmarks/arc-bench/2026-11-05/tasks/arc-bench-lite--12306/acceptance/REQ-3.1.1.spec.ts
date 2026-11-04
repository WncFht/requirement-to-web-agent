// requirement: REQ-3.1.1
import { expect } from '@playwright/test';
import { test } from './fixtures/test';
import { entry, region, login, center } from './helpers';

test("REQ-3.1.1: Open authenticated personal center", async ({ page }) => {
  await entry(page);
  await login(page, 'personal_center_user');
  await center(page);
  await expect(page.getByRole('navigation', { name: 'Personal center menu', exact: true })).toBeVisible();
  await expect(region(page, 'Notice')).toContainText('personal_center_user');
});
