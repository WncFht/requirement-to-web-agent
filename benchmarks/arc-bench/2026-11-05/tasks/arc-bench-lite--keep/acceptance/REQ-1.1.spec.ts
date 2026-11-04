// requirement: REQ-1.1
import { test, expect, action, openHome } from './helpers';

test('REQ-1.1: Open the workspace', async ({ page }) => {
  await openHome(page);
  const sidebar = page.getByRole('navigation', { name: 'Sidebar', exact: true });
  await expect(sidebar).toBeVisible();
  await expect(action(page, 'Toggle sidebar')).toHaveAttribute('aria-expanded', 'true');
  for (const name of ['Notes', 'Archived']) {
    await expect(action(sidebar, name)).toBeVisible();
  }
  await expect(action(sidebar, 'Notes')).toHaveAttribute('aria-current', 'true');
});
