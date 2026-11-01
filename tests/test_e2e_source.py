"""Reject fixture-based E2E false RED before freezing acceptance scenarios."""

import os
import unittest
from unittest.mock import patch

from infrastructure.stages.frontend.interactions.testing import (
    validate_e2e_source,
    backend_cookie_names,
)
from pathlib import Path
from tempfile import TemporaryDirectory


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
        with patch.dict(os.environ, {"ARC_LEGACY_E2E_COOKIE_NAMES": "1"}):
            validate_e2e_source(source, ["session_id"])

    def test_cookie_producer_constants_and_literals_are_supplied(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "backend/src").mkdir(parents=True)
            (root / "backend/src/session.ts").write_text(
                'const COOKIE = "session_id"; const header = `${COOKIE}=${id}`; const other = `other_session=${token}`;'
            )
            self.assertEqual(
                backend_cookie_names(root), ["other_session", "session_id"]
            )

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
