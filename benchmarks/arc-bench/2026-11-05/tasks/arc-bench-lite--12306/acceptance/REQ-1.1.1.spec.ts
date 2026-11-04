// requirement: REQ-1.1.1
import { expect } from '@playwright/test';
import { test } from './fixtures/test';
import { entry, link, button } from './helpers';

test("REQ-1.1.1: Open credential login", async ({ page }) => {
  await entry(page);
  await link(page, 'Login').click();
  await expect(page.getByPlaceholder('Email/Username/Mobile number', { exact: true })).toBeVisible();
  await expect(page.getByPlaceholder('Password', { exact: true })).toBeVisible();
  await expect(button(page, 'LOGIN')).toBeVisible();
});
