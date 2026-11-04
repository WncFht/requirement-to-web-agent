// requirement: REQ-2.1
import { test, expect } from '@playwright/test';
import { home, region, count, men } from './helpers';

test("REQ-2.1: Inspect category and breadcrumb", async ({ page }) => {
  await home(page); await men(page);
  await expect(page.getByRole('heading', { name: 'Men', exact: true })).toBeVisible();
  await expect(region(page, 'Category description')).toContainText('Men');
  const breadcrumb = page.getByRole('navigation', { name: 'Breadcrumb', exact: true });
  await expect(breadcrumb).toHaveText(/Home\s*.*CLOTHES\s*.*Men/);
  await expect(count(page)).toBeVisible();
  await expect(page.getByRole('combobox', { name: 'Sort by', exact: true })).toBeVisible();
  await expect(region(page, 'Product list')).toBeVisible();
});
