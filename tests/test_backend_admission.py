"""Impossible assertions are rejected before entering frozen RED/GREEN."""

import unittest
from unittest.mock import Mock
from infrastructure.stages.backend.test_admission import (
    validate_backend_test,
    review_backend_test,
)

BAD = """function readSafe(headers: Record<string, string | string[]> | undefined): string {
  return JSON.stringify(headers ?? {});
}
assert.ok(!readSafe(result.headers));
"""


class BackendAdmissionTests(unittest.TestCase):
    def test_independent_contradiction_rejects_candidate_without_editing_it(self):
        model = Mock()
        model.generate_json.return_value = {
            "status": "CONTRADICTORY",
            "reason": "Helper forbids a supplied object key",
        }
        with self.assertRaisesRegex(ValueError, "before freezing"):
            review_backend_test(BAD, model, {})
        self.assertEqual(model.generate_json.call_args.args[1]["source"], BAD)

    def test_review_does_not_admit_unknown_or_empty_verdicts(self):
        for verdict in [
            {},
            {"status": "UNKNOWN", "reason": "uncertain"},
            {"status": "NO_CONTRADICTION_FOUND", "reason": ""},
        ]:
            with (
                self.subTest(verdict=verdict),
                self.assertRaisesRegex(ValueError, "invalid verdict"),
            ):
                review_backend_test(
                    "candidate", Mock(generate_json=Mock(return_value=verdict)), {}
                )

    def test_clean_review_preserves_other_gates(self):
        model = Mock(
            generate_json=Mock(
                return_value={
                    "status": "NO_CONTRADICTION_FOUND",
                    "reason": "No conflicting assertions identified",
                }
            )
        )
        self.assertEqual(
            review_backend_test("candidate", model, {})["status"],
            "NO_CONTRADICTION_FOUND",
        )

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
