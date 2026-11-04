// requirement: REQ-5.5
import { test, expect } from '@playwright/test';
import { home, nav, action, region, expectMoney, checkoutSetup, paymentStep, placeOrder } from './helpers';

test("REQ-5.5: Place order for selected product", async ({ page }) => {
  await home(page); const product = 'Hummingbird order-confirmation t-shirt'; await checkoutSetup(page, 'checkout_6_6_user', product); await paymentStep(page); await placeOrder(page);
  await expect(page.getByRole('heading', { name: 'Order confirmation', exact: true })).toBeVisible(); await expect(region(page, 'Order details')).toContainText(product);
});

test("REQ-5.5: Inspect completed order and continue shopping", async ({ page }) => {
  await home(page); const product = 'Hummingbird order-complete t-shirt'; await checkoutSetup(page, 'checkout_6_7_user', product); await paymentStep(page); await placeOrder(page);
  await expect(page.getByRole('heading', { name: 'Order confirmation', exact: true })).toBeVisible(); await expect(region(page, 'Order reference')).toContainText(/\S+/);
  const details = region(page, 'Order details'); for (const text of [product, 'Delivery', 'Bank wire', '1 Commerce Road']) await expect(details).toContainText(text);
  await expect(details).toContainText(/Quantity\s*:?\s*1/); await expectMoney(region(details, 'Total'), 33);
  await action(page, 'Continue shopping').click(); await expect(page.getByRole('heading', { name: 'Popular Products', exact: true })).toBeVisible();
  await expect(nav(page).getByRole('searchbox', { name: 'Search', exact: true })).toBeVisible(); for (const name of ['My account', 'Cart']) await expect(action(nav(page), name)).toBeVisible();
});
