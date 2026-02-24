#!/usr/bin/env python3
"""Check overflow/page-coherence outcomes for translated artifacts (T05.3)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def check_record(rec: Dict[str, Any]) -> Dict[str, Any]:
    reasons: List[str] = []

    src = rec.get("source_pages")
    out = rec.get("output_pages")
    overflow_mode = rec.get("overflow_mode", "none")
    overflow_reported = bool(rec.get("overflow_reported", False))

    if not isinstance(src, int) or src <= 0:
        reasons.append("invalid_source_pages")
    if not isinstance(out, int) or out <= 0:
        reasons.append("invalid_output_pages")

    if not reasons:
        if out < src:
            reasons.append("output_pages_less_than_source")
        if out != src:
            if overflow_mode not in {"flow_to_next_page", "rescale", "hybrid"}:
                reasons.append("missing_overflow_policy")
            if not overflow_reported:
                reasons.append("overflow_not_reported")

    return {
        "run_id": rec.get("run_id"),
        "job_id": rec.get("job_id"),
        "file_id": rec.get("file_id"),
        "source_pages": src,
        "output_pages": out,
        "status": "PASS" if not reasons else "FAIL",
        "reasons": reasons,
    }


def summarize(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    failed = sum(1 for r in results if r["status"] == "FAIL")
    return {
        "total": len(results),
        "passed": len(results) - failed,
        "failed": failed,
        "status": "PASS" if failed == 0 else "FAIL",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check page coherence and overflow handling")
    parser.add_argument("records", type=Path, help="JSON array of page-count records")
    parser.add_argument("--output", type=Path, default=Path("logs/page-coherence.json"))
    args = parser.parse_args()

    records = json.loads(args.records.read_text())
    if isinstance(records, dict):
        records = [records]

    results = [check_record(r) for r in records]
    summary = summarize(results)
    payload = {"summary": summary, "results": results}

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"status": summary["status"], "failed": summary["failed"], "output": str(args.output)}))
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
