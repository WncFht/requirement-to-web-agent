"""Reject fixture-based E2E false RED before freezing acceptance scenarios."""

import os
import unittest
from unittest.mock import patch

from infrastructure.stages.frontend.interactions.testing import validate_e2e_source


class E2ESourceTests(unittest.TestCase):
    def test_real_browser_scenario_is_accepted(self):
        validate_e2e_source(
            'await page.goto("/register"); await page.getByRole("button").click();'
        )

    @patch.dict(os.environ, {"ARC_LEGACY_E2E_SOURCE_CHECK": "0"})
    def test_fixture_injection_is_rejected_before_freezing(self):
        source = "await page.evaluate(() => { window.__ARC_UI_FIXTURE__ = {}; }); await page.reload();"
        with self.assertRaisesRegex(ValueError, "reserved"):
            validate_e2e_source(source)

    @patch.dict(os.environ, {"ARC_LEGACY_E2E_SOURCE_CHECK": "1"})
    def test_legacy_switch_restores_previous_fixture_admission(self):
        validate_e2e_source("window.__ARC_UI_FIXTURE__ = {};")

    @patch.dict(os.environ, {"ARC_LEGACY_E2E_SOURCE_CHECK": "1"})
    def test_legacy_switch_keeps_existing_host_guard(self):
        with self.assertRaisesRegex(ValueError, "loopback"):
            validate_e2e_source('await page.goto("http://localhost:3000/");')
