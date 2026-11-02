"""Execute unchanged fixed14 against either engine without legacy IR dependencies."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.evaluation import evaluate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--mode", choices=("fixed", "production"), default="fixed")
    parser.add_argument("--adapter", type=Path)
    args = parser.parse_args()
    result = evaluate(
        args.output,
        args.evidence,
        args.mode,
        json.loads(args.adapter.read_text()) if args.adapter else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "GREEN" else 1)


if __name__ == "__main__":
    main()
