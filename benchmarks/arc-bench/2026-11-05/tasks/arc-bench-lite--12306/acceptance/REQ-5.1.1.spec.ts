// requirement: REQ-5.1.1
import { expect } from '@playwright/test';
import { test } from './fixtures/test';
import { entry, button, region, booking } from './helpers';

test("REQ-5.1.1: Open selected-journey booking form", async ({ page }) => {
  await entry(page);
  await booking(page, 'bookable_user');
  await expect(region(page, 'Train Information')).toContainText('G1001');
  await expect(button(page, 'Place order')).toBeVisible();
});
