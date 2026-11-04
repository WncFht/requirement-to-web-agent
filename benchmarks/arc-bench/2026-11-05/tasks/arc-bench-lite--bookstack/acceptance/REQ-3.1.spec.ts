// requirement: REQ-3.1
import { test, expect } from '@playwright/test';
import { identity, enter, region, entry, heading, createBook, createPage } from './helpers';

test("REQ-3.1: Publish a page", async ({ page }, testInfo) => {
  const id = identity(testInfo);
  await enter(page);
  const book = await createBook(page, id, 'Book 6.1.1');
  const name = await createPage(page, id, book, 'Page Created 6.1.1', 'Page content created by corresponding prerequisite behavior.');
  await heading(page, book);
  await expect(entry(region(page, 'Page list'), name)).toHaveCount(1);
});
