// requirement: REQ-2.2
import { test } from '@playwright/test';
import { text, identity, enter, heading, createBook, openBook } from './helpers';

test("REQ-2.2: Open from global list", async ({ page }, testInfo) => {
  const id = identity(testInfo);
  await enter(page);
  const name = await createBook(page, id, 'Book 5.2.1');
  await openBook(page, name);
  await heading(page, name);
  await text(page, 'Reference book description.');
});
