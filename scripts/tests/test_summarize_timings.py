"""Keep interrupted attempts and inclusive spans distinct from pipeline wall time."""

import gzip
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from summarize_timings import summarize


class TimingSummaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "timings.jsonl"

    def row(self, span, kind, event, seconds=0, **extra):
        return {
            "version": 1,
            "trace_id": "trace",
            "span_id": span,
            "parent_id": None,
            "pid": 1,
            "kind": kind,
            "stage": "Stage12",
            "name": None,
            "event": event,
            "timestamp": "time",
            "elapsed_seconds": seconds,
            "status": "ok",
            **extra,
        }

    def write(self, rows):
        self.path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")

    def test_parents_not_added_to_categories_and_failed_attempts_retained(self):
        rows = []
        for span, kind, seconds in [
            ("entry", "entrypoint", 20),
            ("pipeline", "pipeline", 17),
            ("stage", "pipeline_stage", 15),
            ("model", "model_request", 8),
            ("gate", "typecheck", 3),
        ]:
            rows += [
                self.row(span, kind, "start"),
                self.row(span, kind, "end", seconds),
            ]
        rows += [
            self.row("failed", "typecheck", "start"),
            self.row("failed", "typecheck", "end", 2, status="nonzero"),
            self.row("skip", "stage_skip", "start"),
            self.row("skip", "stage_skip", "end", 0.01, status="skipped"),
        ]
        self.write(rows)
        result = summarize(self.path)["traces"]["trace"]
        self.assertEqual(result["entrypoint_seconds"], [20])
        self.assertEqual(result["pipeline_seconds"], [17])
        self.assertEqual(result["categories"]["typecheck"]["seconds"], 5)
        self.assertEqual(result["categories"]["typecheck"]["nonzero"], 1)
        self.assertNotIn("pipeline_stage", result["categories"])
        self.assertEqual(result["skipped_stages"], ["Stage12"])

    def test_missing_end_and_orphan_end_are_unknown_not_zero(self):
        self.write(
            [
                self.row("killed", "model_request", "start"),
                self.row("orphan", "build", "end", 4),
            ]
        )
        result = summarize(self.path)["traces"]["trace"]
        self.assertEqual(result["incomplete_span_ids"], ["killed"])
        self.assertEqual(result["orphan_end_span_ids"], ["orphan"])
        self.assertEqual(result["categories"], {})

    def test_resume_traces_do_not_overwrite_prior_attempts(self):
        self.write(
            [
                self.row("stage", "pipeline_stage", "start"),
                self.row("stage", "pipeline_stage", "end", 3, status="error"),
                self.row("stage2", "pipeline_stage", "start", trace_id="resume"),
                self.row("stage2", "pipeline_stage", "end", 2, trace_id="resume"),
            ]
        )
        result = summarize(self.path)["traces"]
        self.assertEqual(result["trace"]["stages"]["Stage12"]["error"], 1)
        self.assertEqual(result["resume"]["stages"]["Stage12"]["ok"], 1)

    def test_corrupt_duplicate_negative_or_nonfinite_records_are_reported(self):
        self.write(
            [
                self.row("a", "build", "start"),
                self.row("a", "build", "start"),
                self.row("b", "build", "end", -1),
                self.row("c", "build", "end", float("nan")),
                self.row("d", "build", "end", True),
            ]
        )
        with self.path.open("a") as stream:
            stream.write('{"torn":\n')
        self.assertEqual(len(summarize(self.path)["malformed_or_duplicate_records"]), 5)

    def test_compressed_log_and_mismatched_span(self):
        self.write(
            [self.row("a", "build", "start"), self.row("a", "typecheck", "end", 1)]
        )
        compressed = self.path.with_suffix(".jsonl.gz")
        with gzip.open(compressed, "wb") as stream:
            stream.write(self.path.read_bytes())
        self.assertEqual(summarize(self.path), summarize(compressed))
        self.assertEqual(summarize(compressed)["traces"]["trace"]["categories"], {})
        self.assertEqual(
            summarize(compressed)["malformed_or_duplicate_records"][0]["error_type"],
            "MismatchedSpan",
        )
