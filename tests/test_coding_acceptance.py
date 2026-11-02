"""Location adapters preserve oracle semantics while accepting ordinary schema metadata."""

import unittest
from coding_agent.acceptance import adapter_from_schema


class AcceptanceAdapterTests(unittest.TestCase):
    def schema(self):
        def field(**values):
            return {
                "type": "string",
                "primary_key": False,
                "nullable": False,
                "references": None,
                "default": None,
            } | values

        columns = [
            "username",
            "password_hash",
            "nationality",
            "name",
            "passport_number",
            "passport_expiration",
            "date_of_birth",
            "gender",
            "email",
            "agreement",
            "created_at",
        ]
        accounts = {n: field() for n in columns}
        accounts["id"] = field(type="integer", primary_key=True)
        sessions = {
            "id": field(type="integer", primary_key=True),
            "account_id": field(type="integer", references="accounts.id"),
            "token": field(),
            "created_at": field(),
        }
        return {
            "accounts": {
                "fields": accounts,
                "sample": {"created_at": "2026-11-02T00:00:00Z"},
            },
            "sessions": {
                "fields": sessions,
                "sample": {"created_at": "2026-11-02T00:00:00Z"},
            },
        }

    def test_required_timestamp_comes_from_real_registration_metadata(self):
        result = adapter_from_schema(
            self.schema(), {"names": [""], "paths": ["/api/auth/me"]}
        )
        self.assertEqual(result["account_fields"]["agreement_consent"], "agreement")
        self.assertEqual(result["account_seed"]["username"], "taken_traveler")
        self.assertEqual(result["account_seed"]["created_at"], "2026-11-02T00:00:00Z")
        self.assertEqual(result["cookie_name"], "")
        self.assertEqual(result["session_seed"]["token"], result["session_token"])

    def test_unknown_business_field_is_never_invented_from_a_sample(self):
        schema = self.schema()
        schema["accounts"]["fields"]["favorite_food"] = schema["accounts"]["fields"][
            "username"
        ].copy()
        schema["accounts"]["sample"]["favorite_food"] = "sample"
        with self.assertRaisesRegex(ValueError, "Unknown required account field"):
            adapter_from_schema(
                schema, {"names": ["session"], "paths": ["/api/auth/me"]}
            )


if __name__ == "__main__":
    unittest.main()
