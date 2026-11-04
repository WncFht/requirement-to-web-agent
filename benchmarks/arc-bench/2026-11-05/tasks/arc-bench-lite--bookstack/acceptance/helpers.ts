import { expect, type Locator, type Page, type TestInfo } from '@playwright/test';
import { randomBytes } from 'node:crypto';

const runId = randomBytes(8).toString('hex');

// Literal scenario titles are unique in this package; normalize them to readable case ids.
export function identity(info: TestInfo): string {
  const caseId = info.title.replace(/[^A-Za-z0-9]+/g, '-');
  return `${runId}-w${info.workerIndex}-${caseId}`;
}
export const named = (id: string, base: string) => `${base} [${id}]`;
export const region = (page: Page, name: string) => page.getByRole('region', { name, exact: true });
export const button = (page: Page, name: string) => page.getByRole('button', { name, exact: true });
// The contract allows either a link or a button. Union does not choose by DOM order.
export const entry = (scope: Page | Locator, name: string) =>
  scope.getByRole('link', { name, exact: true }).or(scope.getByRole('button', { name, exact: true }));
export async function enter(page: Page) {
  await page.goto('/');
}
export async function go(page: Page, name: string) {
  // The main navigation exposes the public Books entry; breadcrumbs need not.
  const navigation = page.getByRole('navigation')
    .filter({ has: page.getByRole('link', { name: 'Books', exact: true }) });
  await navigation.getByRole('link', { name, exact: true }).click();
}
export async function heading(page: Page, name: string) {
  await expect(page.getByRole('heading', { name, exact: true })).toBeVisible();
}
export async function text(page: Page, value: string) {
  await expect(page.getByText(value, { exact: true })).toBeVisible();
}
export async function metadata(page: Page, name: string, description: string, tags: string) {
  await page.getByLabel('Name', { exact: true }).fill(name);
  await page.getByLabel('Description', { exact: true }).fill(description);
  await page.getByLabel('Tags', { exact: true }).fill(tags);
}
export async function openBook(page: Page, name: string) {
  await go(page, 'Books');
  await entry(region(page, 'Book list'), name).click();
  await heading(page, name);
}
export async function beginBook(page: Page) {
  await go(page, 'Books');
  await entry(page, 'Create New Book').click();
}
export async function createBook(page: Page, id: string, base: string, description = 'Reference book description.', tags = 'manual, handbook') {
  const name = named(id, base);
  await beginBook(page);
  await metadata(page, name, description, tags);
  await button(page, 'Save Book').click();
  await heading(page, name);
  return name;
}
export async function createPage(page: Page, id: string, book: string, base: string, content: string) {
  await openBook(page, book);
  await button(page, 'New Page').click();
  const name = named(id, base);
  await page.getByPlaceholder('Page title', { exact: true }).fill(name);
  await page.getByPlaceholder('Write your page content here...', { exact: true }).fill(content);
  await button(page, 'Save Page').click();
  await heading(page, book);
  await expect(entry(region(page, 'Page list'), name)).toHaveCount(1);
  await expect(entry(region(page, 'Page list'), name)).toBeVisible();
  return name;
}
