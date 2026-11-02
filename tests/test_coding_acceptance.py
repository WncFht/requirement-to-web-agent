"""Location adapters preserve oracle semantics while accepting ordinary schema metadata."""

import unittest
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.evaluation import adapter_from_schema, evaluation_directory


class AcceptanceAdapterTests(unittest.TestCase):
    def test_startup_failure_preserves_service_logs_before_temporary_cleanup(self):
        with TemporaryDirectory() as tmp:
            evidence = Path(tmp)
            with self.assertRaisesRegex(ValueError, "startup failed"):
                with evaluation_directory(evidence) as directory:
                    self.assertIn("teacher-acceptance-", str(directory))
                    (directory / "server-0.log").write_text("SQLite ABI mismatch")
                    raise ValueError("startup failed")
            self.assertFalse(directory.exists())
            self.assertEqual(
                (evidence / "server-0.log").read_text(), "SQLite ABI mismatch"
            )

    def test_hashed_session_is_adapted_only_after_actual_cookie_storage_proof(self):
        schema = self.schema()
        fields = schema["sessions"]["fields"]
        fields["token_hash"] = fields.pop("token")
        schema["sessions"]["sample"]["token_hash"] = hashlib.sha256(
            b"observed-cookie"
        ).hexdigest()
        transport = {
            "names": ["session"],
            "paths": ["/api/session"],
            "cookies": [{"name": "session", "value": "observed-cookie"}],
        }
        result = adapter_from_schema(schema, transport)
        self.assertEqual(
            result["session_seed"]["token_hash"],
            hashlib.sha256(result["session_token"].encode()).hexdigest(),
        )
        transport["cookies"][0]["value"] = "different"
        with self.assertRaisesRegex(ValueError, "not proved"):
            adapter_from_schema(schema, transport)

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

    def test_text_primary_key_can_be_the_session_credential(self):
        schema = self.schema()
        fields = schema["sessions"]["fields"]
        fields.pop("token")
        fields["id"]["type"] = "string"
        result = adapter_from_schema(
            schema, {"names": ["session_id"], "paths": ["/api/session"]}
        )
        self.assertEqual(result["session_seed"]["id"], result["session_token"])
        fields["id"]["type"] = "integer"
        with self.assertRaisesRegex(ValueError, "Ambiguous actual session schema"):
            adapter_from_schema(
                schema, {"names": ["session_id"], "paths": ["/api/session"]}
            )


if __name__ == "__main__":
    unittest.main()
