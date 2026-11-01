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

    def test_json_serialization_cannot_equal_unquoted_credential(self):
        for assertion in (
            'assert.equal("cred-unknown", JSON.stringify(body));',
            "assert.strictEqual(JSON.stringify(body), 'cred-unknown');",
        ):
            with (
                self.subTest(assertion=assertion),
                self.assertRaisesRegex(ValueError, "non-JSON"),
            ):
                validate_backend_test(assertion)

    def test_valid_json_and_negative_membership_are_allowed(self):
        validate_backend_test("assert.equal(JSON.stringify(body), '{}');")
        validate_backend_test(
            'assert.equal(JSON.stringify(body).includes("cred-unknown"), false);'
        )

    @patch.dict(os.environ, {"ARC_LEGACY_TEST_SANITY": "1"})
    def test_legacy_flag_restores_previous_admission(self):
        validate_backend_test(BAD)
