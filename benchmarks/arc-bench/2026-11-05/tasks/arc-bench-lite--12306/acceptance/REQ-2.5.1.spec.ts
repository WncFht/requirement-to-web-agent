// requirement: REQ-2.5.1

import { test } from './fixtures/test';
import { entry, search, sortTrains } from './helpers';
test("REQ-2.5.1: Toggle Departure Time sorting", async ({ page }) => {
    await entry(page);
    await search(page);
    await sortTrains(page, "Departure Time", "departure");
});
