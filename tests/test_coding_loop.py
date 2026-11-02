"""Global budget, no-progress, admission and observability control-flow regressions."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from coding_agent.config import Config
from coding_agent.loop import run, progress_key
from coding_agent.protocol import BudgetExhausted


class NoChecks:
    def __init__(self, output, trace, remaining):
        self.reports = {}
        self.frozen = None

    def install(self):
        pass

    def execute(self, args):
        return {"stdout": "fixture-node"}


class RepeatRead:
    def __init__(self, config, trace):
        self.trace = trace

    def generate(self, messages, remaining):
        action = {"action": "read", "paths": ["frontend/src/App.tsx"]}
        return action, json.dumps(action)


class Exhausted:
    def __init__(self, config, trace):
        pass

    def generate(self, messages, remaining):
        raise BudgetExhausted("fixture allowance")


class CodingLoopTests(unittest.TestCase):
    def test_check_timing_noise_is_not_progress_but_new_result_or_edit_is(self):
        with TemporaryDirectory() as tmp:
            output = Path(tmp)
            path = output / "source.ts"
            path.write_text("before")
            action = {"action": "check", "name": "backend"}
            response = {
                "status": "OK",
                "summary": "Actual check results",
                "checks": {
                    "name": "backend",
                    "status": "FAILED",
                    "passed": 1,
                    "failed": 2,
                    "output": "duration 1",
                    "seconds": 1.0,
                },
            }
            before = progress_key(output, "IMPLEMENT", action, response)
            response["checks"].update(output="duration 2", seconds=2.0)
            self.assertEqual(
                before, progress_key(output, "IMPLEMENT", action, response)
            )
            response["checks"]["passed"] = 2
            self.assertNotEqual(
                before, progress_key(output, "IMPLEMENT", action, response)
            )
            response["checks"]["passed"] = 1
            path.write_text("after")
            self.assertNotEqual(
                before, progress_key(output, "IMPLEMENT", action, response)
            )

    def test_repeated_unchanged_reads_stop_after_three_and_preserve_failure(self):
        self.check(RepeatRead, "NO_PROGRESS", 3)

    def test_token_budget_stops_with_explicit_terminal_result(self):
        self.check(Exhausted, "BUDGET_EXHAUSTED", 1)

    def check(self, model, status, turns):
        with TemporaryDirectory() as tmp:
            p = Path(tmp)
            inputs = p / "input"
            inputs.mkdir()
            (inputs / "requirements.yaml").write_text("id: R\n")
            output = p / "output"

            # The fake installer writes an empty lock to reproduce the real install boundary.
            class FakeChecks(NoChecks):
                def install(self):
                    (output / "package-lock.json").write_text("{}")

            config = Config(
                inputs, output, base_url="http://unused.invalid", api_key="fixture"
            )
            result = run(config, model_factory=model, checks_factory=FakeChecks)
            self.assertEqual(result["status"], status, result)
            self.assertEqual(result["turns"], turns)
            self.assertTrue((output / ".arc/agent/artifact-manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
