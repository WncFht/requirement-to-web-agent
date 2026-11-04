// requirement: REQ-3.3.1
import { expect } from '@playwright/test';
import { test } from './fixtures/test';
import { entry, button, row, orders, orderSetup } from './helpers';

test("REQ-3.3.1: Open unpaid-order view", async ({ page }) => {
  await entry(page);
  await orderSetup(page, 'orders_unpaid_user');
  await orders(page, 'Uncompleted orders');
  await expect(button(row(page, 'G1001'), 'Pay')).toBeVisible();
});
