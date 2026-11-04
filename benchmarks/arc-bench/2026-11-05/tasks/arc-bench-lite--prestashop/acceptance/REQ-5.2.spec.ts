// requirement: REQ-5.2
import { test, expect } from '@playwright/test';
import { home, action, region, checkoutSetup, STEP } from './helpers';

test("REQ-5.2: Select Home address", async ({ page }) => {
  await home(page); await checkoutSetup(page, 'checkout_address_user', STEP); const addresses = region(page, 'Addresses');
  const radio = addresses.getByRole('radio', { name: 'Home', exact: true }); await radio.check(); await expect(radio).toBeChecked();
  await expect(addresses).toContainText('1 Commerce Road'); await action(addresses, 'Continue').click();
  await expect(region(page, 'Shipping Method')).toBeVisible(); await expect(region(page, 'Order summary')).toContainText(STEP);
});
