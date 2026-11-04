// requirement: REQ-5.1
import { test, expect } from '@playwright/test';
import { accountForCase } from './fixtures/case-accounts';
import { home, action, region, cartSetup, login, createAddress, addressesStep, STEP } from './helpers';

test("REQ-5.1: Start anonymous checkout", async ({ page }) => {
  await home(page); await cartSetup(page, STEP); await action(page, 'Proceed to checkout').click();
  await expect(region(page, 'Personal Information')).toBeVisible(); await expect(region(page, 'Order summary')).toContainText(STEP);
});

test("REQ-5.1: Inspect signed-in customer", async ({ page }) => {
  await home(page); await login(page, 'checkout_user'); await createAddress(page, 'Home'); await cartSetup(page, STEP); await action(page, 'Proceed to checkout').click();
  await expect(region(page, 'Personal Information')).toContainText(accountForCase('prestashop_checkout_user@example.com', test.info().title)); await addressesStep(page);
  await expect(region(page, 'Addresses')).toBeVisible();
});
