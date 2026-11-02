"""Reject fixture-based E2E false RED before freezing acceptance scenarios."""

import unittest

from infrastructure.stages.frontend.interactions.testing import (
    validate_e2e_source,
)


class E2ESourceTests(unittest.TestCase):
    def test_positive_existing_session_cannot_use_a_guessed_cookie_name(self):
        source = 'test("valid session restores identity", async ({page}) => { await page.context().addCookies([{name: "session", value: "id", url: baseURL!}]); });'
        with self.assertRaisesRegex(ValueError, "tested backend producers"):
            validate_e2e_source(source, ["session_id"])
        validate_e2e_source(
            source.replace('name: "session"', 'name: "session_id"'), ["session_id"]
        )
        validate_e2e_source(
            source.replace("valid session", "unknown session"), ["session_id"]
        )

    def test_real_browser_scenario_is_accepted(self):
        validate_e2e_source(
            'await page.goto("/register"); await page.getByRole("button").click();'
        )

    def test_fixture_injection_is_rejected_before_freezing(self):
        source = "await page.evaluate(() => { window.__ARC_UI_FIXTURE__ = {}; }); await page.reload();"
        with self.assertRaisesRegex(ValueError, "reserved"):
            validate_e2e_source(source)

    def test_existing_host_guard(self):
        with self.assertRaisesRegex(ValueError, "loopback"):
            validate_e2e_source('await page.goto("http://localhost:3000/");')
