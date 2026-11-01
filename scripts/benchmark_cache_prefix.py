"""Matched live Stage11 requests: same information, only JSON ordering differs."""

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import random
import sys
from time import monotonic
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from infrastructure.shared.models.text import TextModel
from infrastructure.stages.frontend.interactions.contracts import validate_contract
from infrastructure.stages.frontend.interactions.design import require_fields
from infrastructure.utils.files import save_json
from infrastructure.utils.presentation.console import DemoConsole
from infrastructure.utils.presentation.logging import console_log
from infrastructure.utils.presentation.model_io import invoke


def variants(arguments, namespace):
    original = deepcopy(arguments)
    original["messages"][0]["content"] += (
        "\nExperiment identifier (no change to task): " + namespace
    )
    candidate = deepcopy(original)
    content = original["messages"][-1]["content"]
    payload = json.loads(content)
    stable = {key: payload[key] for key in ("frontend_data", "page_inventory")}
    candidate["messages"][-1]["content"] = json.dumps(
        {**stable, **payload}, ensure_ascii=False
    )
    assert json.loads(candidate["messages"][-1]["content"]) == payload
    assert set(payload) == set(json.loads(candidate["messages"][-1]["content"]))
    return original, candidate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pairs", type=int, default=6)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Refusing to overwrite a cache experiment")
    if args.pairs < 2:
        parser.error("Use at least two distinct event pairs")
    cases = []
    seen = set()
    for line in args.log.read_text(encoding="utf-8-sig").splitlines():
        row = json.loads(line)
        if row.get("event") != "request" or not row.get("stage", "").startswith(
            "Stage 11"
        ):
            continue
        arguments = row["arguments"]
        content = arguments["messages"][-1]["content"]
        if not isinstance(content, str):
            continue
        payload = json.loads(content)
        if (
            "event_id" in payload
            and "frontend_data" in payload
            and "page_inventory" in payload
            and "correction" not in payload
            and payload["event_id"] not in seen
        ):
            cases.append((row, payload))
            seen.add(payload["event_id"])
    if len(cases) < args.pairs + 1:
        parser.error("Not enough distinct first-attempt event requests in source log")
    cases = cases[: args.pairs + 1]
    reference = {key: cases[0][1][key] for key in ("frontend_data", "page_inventory")}
    if any(
        any(payload[key] != reference[key] for key in reference) for _, payload in cases
    ):
        parser.error("Requests do not share identical stable context")
    args.output.mkdir(parents=True, exist_ok=False)
    namespace = uuid4().hex
    experiment = {
        "protocol": "Distinct matched event requests. One warm-up per variant on a separate event, then counterbalanced A/B order. Shared unique system suffix avoids prior full-payload cache warming. All fields and values identical within each pair; outputs checked by the original Stage11 contract validator. No application output modified.",
        "namespace": namespace,
        "source_log_sha256": sha256(args.log.read_bytes()).hexdigest(),
        "warmup": [],
        "pairs": [],
        "limitations": "Single best-effort provider/proxy trial; no certainty about routing or persistence. Stage11 contract structure checks do not establish full application behavior; independent full generation remains required.",
    }
    save_json(args.output / "experiment.json", experiment)
    model = TextModel()
    console = DemoConsole()
    rng = random.Random(4810)
    with console_log(args.output):
        for index, (row, payload) in enumerate(cases):
            pair = {
                "source_call_id": row["call_id"],
                "event_id": payload["event_id"],
                "results": {},
            }
            requests = variants(row["arguments"], namespace)
            order = [0, 1] if index % 2 == 0 else [1, 0]
            if index == 0:
                rng.shuffle(order)
            pair["order"] = order
            for variant in order:
                arguments = requests[variant]
                if arguments["model"] != model.name:
                    raise ValueError(
                        "Configured model differs from recorded source model"
                    )
                label = "control" if variant == 0 else "stable_first"
                console.show(
                    f"Cache pair {index} {label}",
                    "Same recorded task, values and validator; request order only.",
                )
                started = monotonic()
                response = invoke(model.client, arguments)
                elapsed = monotonic() - started
                content = response.choices[0].message.content
                value = json.loads(content)
                require_fields(value, {"contract"}, "Event contract response")
                validate_contract(payload["event_id"], value["contract"])
                usage = response.model_dump(mode="json").get("usage")
                pair["results"][label] = {
                    "usage": usage,
                    "elapsed_seconds": elapsed,
                    "validator": "PASSED",
                }
                if index == 0:
                    experiment["warmup"].append(
                        {"variant": label, **pair["results"][label]}
                    )
                save_json(args.output / "experiment.json", experiment)
            if index:
                experiment["pairs"].append(pair)
                save_json(args.output / "experiment.json", experiment)
    totals = {}
    for variant in ("control", "stable_first"):
        records = [pair["results"][variant] for pair in experiment["pairs"]]
        totals[variant] = {
            key: sum(record["usage"].get(key, 0) or 0 for record in records)
            for key in (
                "prompt_tokens",
                "prompt_cache_hit_tokens",
                "prompt_cache_miss_tokens",
                "completion_tokens",
                "total_tokens",
            )
        }
        totals[variant]["elapsed_seconds"] = sum(
            record["elapsed_seconds"] for record in records
        )
        totals[variant]["input_cache_hit_ratio"] = (
            totals[variant]["prompt_cache_hit_tokens"]
            / totals[variant]["prompt_tokens"]
        )
    experiment["totals"] = totals
    save_json(args.output / "experiment.json", experiment)
    print(json.dumps(totals, indent=2))


if __name__ == "__main__":
    main()
