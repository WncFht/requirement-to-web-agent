// requirement: REQ-1.1
import { test, expect } from '@playwright/test';
import { enter } from './helpers';

test("REQ-1.1: Open the book workspace", async ({ page }) => {
  await enter(page);
  await expect(page.getByRole('link', { name: 'Books', exact: true })).toBeVisible();
  await page.getByRole('link', { name: 'Books', exact: true }).click();
  await expect(page.getByRole('region', { name: 'Book list', exact: true })).toBeVisible();
});
