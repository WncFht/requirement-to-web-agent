"""Impossible assertions are rejected before entering frozen RED/GREEN."""

import os
import unittest
from unittest.mock import patch
from infrastructure.stages.backend.test_admission import validate_backend_test

BAD = """function readSafe(headers: Record<string, string | string[]> | undefined): string {
  return JSON.stringify(headers ?? {});
}
assert.ok(!readSafe(result.headers));
"""


class BackendAdmissionTests(unittest.TestCase):
    @patch.dict(os.environ, {"ARC_LEGACY_TEST_SANITY": "0"})
    def test_actual_impossible_helper_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Contradictory"):
            validate_backend_test(BAD)

    def test_property_absence_and_normal_negation_remain_allowed(self):
        validate_backend_test('assert.ok(!result.headers?.["set-cookie"]);')
        validate_backend_test(
            "function hasCookie(x) { return Boolean(x.cookie); } assert.ok(!hasCookie(headers));"
        )

    @patch.dict(os.environ, {"ARC_LEGACY_TEST_SANITY": "1"})
    def test_legacy_flag_restores_previous_admission(self):
        validate_backend_test(BAD)
