// requirement: REQ-2.7

import { test } from './fixtures/test';
import { entry, link, defaultResults } from './helpers';
test("REQ-2.7: Open Tickets quick entry", async ({ page }) => {
    await entry(page);
    await link(page.getByRole('navigation'), 'Booking').hover();
    await link(page, 'Tickets').click();
    await defaultResults(page);
});
