// requirement: REQ-5.3
import { test, expect } from '@playwright/test';
import { home, region, expectMoney, checkoutSetup, shippingStep, STEP } from './helpers';

test("REQ-5.3: Use separate invoice address", async ({ page }) => {
  await home(page); await checkoutSetup(page, 'checkout_invoice_user', STEP);
  await region(page, 'Addresses').getByRole('checkbox', { name: 'Use same address', exact: true }).uncheck();
  await expect(region(page, 'Invoice address')).toBeVisible(); await expect(region(page, 'Invoice address')).toContainText('Home');
});

test("REQ-5.3: Choose Delivery", async ({ page }) => {
  await home(page); await checkoutSetup(page, 'checkout_invoice_user', STEP); await shippingStep(page);
  const shipping = region(page, 'Shipping Method'); await expect(shipping.getByRole('radio', { name: 'Delivery', exact: true })).toBeVisible();
  await expectMoney(region(shipping, 'Shipping cost'), 5); await shipping.getByRole('radio', { name: 'Delivery', exact: true }).check();
  await expect(shipping.getByRole('radio', { name: 'Delivery', exact: true })).toBeChecked();
  await expect(region(page, 'Order summary')).toContainText(STEP); await expectMoney(region(region(page, 'Order summary'), 'Total'), 31);
});
