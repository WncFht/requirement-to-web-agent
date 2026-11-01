"""A failed/early attempt is counted and cannot masquerade as accepted fast output."""

from copy import deepcopy
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run_factorial_campaign import schedule, success, model_usage, fingerprint_tree


class FactorialCampaignTests(unittest.TestCase):
    def test_predeclared_schedule_is_reproducible_balanced_and_blocked(self):
        rows = schedule()
        self.assertEqual(rows, schedule())
        self.assertEqual(len(rows), 12)
        self.assertEqual(len({row["name"] for row in rows}), 12)
        for block in (1, 2, 3):
            self.assertEqual(
                {row["arm"] for row in rows if row["block"] == block},
                {"00", "10", "01", "11"},
            )
        for arm in ("00", "10", "01", "11"):
            self.assertEqual(sum(row["arm"] == arm for row in rows), 3)

    def fixture(self):
        accepted = {
            "status": "GREEN",
            "stats": {"expected": 14, "unexpected": 0, "skipped": 0, "flaky": 0},
            "production_build_passed": True,
            "all_preserved_gates_green": True,
        }
        return {
            "phases": {
                name: {"status": "finished", "returncode": 0}
                for name in ("generation", "fixed", "production")
            },
            "gates": {
                name: {"status": "GREEN"}
                for name in ("backend_tdd", "ui_checks", "frontend_e2e")
            },
            "fixed": deepcopy(accepted),
            "production": deepcopy(accepted),
        }

    def test_all_phases_gates_and_both_fixed_and_production_are_required(self):
        self.assertTrue(success(self.fixture()))
        for case in (
            "missing_production",
            "timeout",
            "failed_gate",
            "skipped",
            "flaky",
            "wrong_count",
            "build_failed",
        ):
            record = self.fixture()
            if case == "missing_production":
                del record["phases"]["production"]
            elif case == "timeout":
                record["phases"]["generation"]["status"] = "timeout"
            elif case == "failed_gate":
                record["gates"]["frontend_e2e"]["status"] = "FAILED"
            elif case in ("skipped", "flaky"):
                record["production"]["stats"][case] = 1
            elif case == "wrong_count":
                record["fixed"]["stats"]["expected"] = 13
            else:
                record["fixed"]["production_build_passed"] = False
            with self.subTest(case=case):
                self.assertFalse(success(record))

    def test_http_mirrors_are_not_double_counted_and_failed_calls_cost_is_unknown(self):
        rows = [
            {"event": "request", "call_id": "a"},
            {"event": "http_response", "call_id": "a", "body": "mirror"},
            {
                "event": "response",
                "call_id": "a",
                "stage": "Stage12",
                "elapsed_seconds": 2,
                "response": {
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 10,
                        "total_tokens": 110,
                        "prompt_cache_hit_tokens": 40,
                        "prompt_cache_miss_tokens": 60,
                    }
                },
            },
            {"event": "request", "call_id": "b"},
            {"event": "error", "call_id": "b", "elapsed_seconds": 3},
            {"event": "request", "call_id": "c"},
            {"event": "response", "call_id": "c", "response": {}},
        ]
        with TemporaryDirectory() as directory:
            path = Path(directory) / "model_calls.jsonl"
            path.write_text(
                "\n".join(json.dumps(row) for row in rows) + '\n{"truncated":'
            )
            result = model_usage(path)
        self.assertEqual(result["totals"]["total_tokens"], 110)
        self.assertEqual(result["totals"]["calls"], 1)
        self.assertEqual(result["totals"]["sdk_error_seconds"], 3)
        self.assertEqual(result["calls_with_unknown_usage"], ["b", "c"])
        self.assertEqual(result["malformed_lines"], [8])

    def test_missing_log_is_not_marked_as_known_free(self):
        with TemporaryDirectory() as directory:
            result = model_usage(Path(directory) / "absent")
        self.assertIsNone(result["log_sha256"])
        self.assertIn("unknown", result["cost_scope"])

    def test_dependency_fingerprint_changes_for_bytes_and_symlink_target(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "a").write_text("one")
            first = fingerprint_tree(root)
            (root / "a").write_text("two")
            second = fingerprint_tree(root)
            self.assertNotEqual(first, second)
            (root / "link").symlink_to("a")
            third = fingerprint_tree(root)
            (root / "link").unlink()
            (root / "link").symlink_to("b")
            self.assertNotEqual(third, fingerprint_tree(root))
