"""Statistics preserve failed costs, weighted caches and block-level pairing."""

from copy import deepcopy
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from summarize_factorial_campaign import (
    arm_summary,
    effects,
    successful_pair_effects,
    summarize,
    wilson,
)
from analyze_cache_prefixes import alternative, common_prefix


def record(arm="00", block=1, accepted=True, tokens=100, seconds=10):
    return {
        "name": f"b{block}-{arm}",
        "arm": arm,
        "block": block,
        "compiler_revision": "frozen",
        "success": accepted,
        "attempt_wall_seconds": seconds,
        "phases": {"generation": {"seconds": seconds}},
        "usage": {
            "totals": {
                "prompt_tokens": tokens,
                "prompt_cache_hit_tokens": tokens / 2,
                "total_tokens": tokens,
            },
            "stages": {},
            "calls_with_unknown_usage": [],
        },
    }


class FactorialSummaryTests(unittest.TestCase):
    def test_failed_attempt_cost_is_included_and_no_success_is_not_free(self):
        result = arm_summary(
            [
                record(accepted=False, tokens=200, seconds=20),
                record(tokens=100, seconds=10),
            ]
        )
        self.assertEqual(result["success_rate"], 0.5)
        self.assertEqual(result["failed_known_tokens"], 200)
        self.assertEqual(
            result["known_tokens_per_accepted_app_including_failures"], 300
        )
        self.assertEqual(result["wall_seconds_per_accepted_app_including_failures"], 30)
        empty = arm_summary([record(accepted=False)])
        self.assertIsNone(empty["known_tokens_per_accepted_app_including_failures"])
        self.assertEqual(empty["successful_generation_wall_seconds"]["n"], 0)

    def test_cache_ratio_is_token_weighted_not_average_percentages(self):
        large = record(tokens=900)
        large["usage"]["totals"]["prompt_cache_hit_tokens"] = 0
        small = record(tokens=100)
        small["usage"]["totals"]["prompt_cache_hit_tokens"] = 100
        self.assertEqual(
            arm_summary([large, small])["cache_all_attempts"]["weighted_hit_ratio"], 0.1
        )

    def test_three_successes_do_not_imply_high_confidence_perfect_reliability(self):
        interval = wilson(3, 3)
        self.assertLess(interval[0], 0.5)
        self.assertAlmostEqual(interval[1], 1)

    def test_factorial_effects_pair_blocks_and_exclude_failed_blocks_only_in_success_view(
        self,
    ):
        rows = [
            record(arm=arm, block=block, tokens=tokens, seconds=tokens / 10)
            for block in (1, 2, 3)
            for arm, tokens in [("00", 100), ("10", 60), ("01", 90), ("11", 50)]
        ]
        result = effects(rows, True)["total_tokens"]["effects"]
        self.assertEqual(result["context_main_effect"]["mean"], -40)
        self.assertEqual(result["prefix_main_effect"]["mean"], -10)
        self.assertEqual(result["interaction"]["mean"], 0)
        self.assertEqual(result["optimized_control_ratio"]["mean"], 0.5)
        rows[0]["success"] = False
        self.assertEqual(effects(rows, True)["total_tokens"]["excluded_blocks"], [1])
        self.assertEqual(effects(rows, False)["total_tokens"]["excluded_blocks"], [])

    def test_missing_attempt_is_incomplete_and_changed_source_rejected(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "protocol.json").write_text(
                json.dumps(
                    {
                        "compiler_revision": "frozen",
                        "arms": {"00": [0, 0]},
                        "schedule": [{"name": "b1-00", "arm": "00", "block": 1}],
                    }
                )
            )
            self.assertFalse(summarize(root)["complete"])
            path = root / "runs/b1-00/result.json"
            path.parent.mkdir(parents=True)
            row = record()
            row["compiler_revision"] = "another"
            path.write_text(json.dumps(row))
            with self.assertRaisesRegex(ValueError, "predeclared"):
                summarize(root)

    def test_successful_pair_survives_unrelated_failure_but_retains_selection_warning(
        self,
    ):
        rows = [
            record(arm="00", tokens=100),
            record(arm="10", accepted=False, tokens=200),
            record(arm="01", tokens=90),
            record(arm="11", tokens=60),
        ]
        result = successful_pair_effects(rows)
        pair = result["optimized_vs_control"]
        self.assertEqual(pair["used_blocks"], [1])
        self.assertEqual(
            pair["metrics"]["total_tokens"]["treatment_control_ratio"]["mean"],
            0.6,
        )
        self.assertIn("selected", pair["interpretation"])
        self.assertEqual(result["context_with_prefix_on"]["used_blocks"], [1])
        excluded = result["context_with_prefix_off"]
        self.assertEqual(excluded["used_blocks"], [])
        self.assertEqual(
            excluded["excluded_blocks"],
            [{"block": 1, "reason": "unsuccessful_pair_member"}],
        )

    def test_successful_pair_distinguishes_missing_and_zero_denominators(self):
        rows = [record(arm="00", tokens=0), record(arm="11", tokens=60)]
        result = successful_pair_effects(rows)
        missing = result["context_with_prefix_off"]
        self.assertEqual(missing["excluded_blocks"][0]["reason"], "missing_pair_member")
        tokens = result["optimized_vs_control"]["metrics"]["total_tokens"]
        self.assertIsNone(tokens["treatment_control_ratio"])
        self.assertEqual(tokens["zero_denominator_blocks"], [1])

    def test_offline_reorder_preserves_information_and_reports_character_prefix_only(
        self,
    ):
        arguments = {
            "messages": [
                {"role": "system", "content": "policy"},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "event_id": "x",
                            "frontend_data": {"large": "shared"},
                            "page_inventory": {},
                            "all_requirement_uses": ["same"],
                            "backend_apis": {},
                            "event": {"value": 1},
                        }
                    ),
                },
            ]
        }
        before = deepcopy(arguments)
        candidate = alternative(arguments)
        self.assertEqual(arguments, before)
        self.assertEqual(
            json.loads(candidate["messages"][-1]["content"]),
            json.loads(arguments["messages"][-1]["content"]),
        )
        self.assertEqual(common_prefix("abcd1", "abcd2"), 4)
        self.assertEqual(common_prefix("ab", "abc"), 2)
