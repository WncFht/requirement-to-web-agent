import { expect, test, type Locator, type Page } from '@playwright/test';
export { test, expect };
export const action = (scope: Page | Locator, name: string) =>
  scope.getByRole('button', { name, exact: true });
export const note = (page: Page, title: string) =>
  page.getByRole('region', { name: title, exact: true });
export const section = (page: Page, name: string) =>
  page.getByRole('region', { name, exact: true });
export const editor = (page: Page) => page.getByRole('dialog', { name: 'Note editor', exact: true });
export const notice = (page: Page, name: string) => page.getByRole('status', { name, exact: true });

export async function openHome(page: Page) {
  await page.goto('/');
  await expect(action(page, 'Take a note')).toBeVisible();
}
export async function navigate(page: Page, name: string) {
  await action(page.getByRole('navigation', { name: 'Sidebar', exact: true }), name).click();
}
export async function beginNote(page: Page) {
  await action(page, 'Take a note').click();
  await expect(editor(page)).toBeVisible();
}
export async function createNote(page: Page, title: string, content: string,
  options: { pinned?: boolean } = {}) {
  await beginNote(page);
  await editor(page).getByRole('textbox', { name: 'Title', exact: true }).fill(title);
  await editor(page).getByRole('textbox', { name: 'Content', exact: true }).fill(content);
  if (options.pinned) await action(editor(page), 'Pin note').click();
  await action(editor(page), 'Close').click();
  await expect(editor(page)).toBeHidden();
  await expectNote(page, title, content);
}
export async function expectNote(page: Page, title: string, content?: string) {
  await expect(note(page, title)).toHaveCount(1);
  await expect(note(page, title)).toBeVisible();
  await expect(note(page, title).getByText(title, { exact: true })).toBeVisible();
  if (content !== undefined) await expect(note(page, title).getByText(content, { exact: true })).toBeVisible();
}
export async function archiveNote(page: Page, title: string) {
  await note(page, title).hover();
  await action(note(page, title), `Archive ${title}`).click();
  await expect(note(page, title)).toBeHidden();
  await expect(notice(page, 'Note archived')).toBeVisible();
}
