"""Measure feedback characters from recoverable historical failures without model calls."""

import argparse
import ast
import gzip
import json
import os
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from infrastructure.shared.agent.loop import (
    CheckFailure,
    compact_feedback,
    repair_feedback,
)


def replay(path):
    samples = []
    candidates = 0
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            record = json.loads(line)
            if record["event"] != "request" or "Stage 12" not in record.get(
                "stage", ""
            ):
                continue
            try:
                payload = json.loads(record["arguments"]["messages"][-1]["content"])
            except (KeyError, IndexError, TypeError, ValueError):
                continue
            for item in payload.get("feedback", []):
                message = item.get("error", "") if isinstance(item, dict) else ""
                if not message.startswith("UI checks are not GREEN: "):
                    continue
                candidates += 1
                try:
                    report = ast.literal_eval(message.split(": ", 1)[1])
                except (ValueError, SyntaxError):
                    continue
                error = CheckFailure("UI checks are not GREEN", report)
                before = compact_feedback({"error": str(error)}, limit=6000)
                with patch.dict(os.environ, {"ARC_FULL_FEEDBACK": "0"}):
                    after = repair_feedback(error)
                samples.append(
                    {
                        "call_id": record["call_id"],
                        "before_characters": len(
                            json.dumps(before, ensure_ascii=False)
                        ),
                        "after_characters": len(json.dumps(after, ensure_ascii=False)),
                    }
                )
    return {
        "source_log": str(path),
        "measurement": "Serialized feedback JSON characters, not model tokens or total prompt size",
        "candidate_reports": candidates,
        "recovered_reports": len(samples),
        "unrecoverable_reports": candidates - len(samples),
        "before_characters": sum(s["before_characters"] for s in samples),
        "after_characters": sum(s["after_characters"] for s in samples),
        "samples": samples,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(replay(args.log), indent=2) + "\n")


if __name__ == "__main__":
    main()
