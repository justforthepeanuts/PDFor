#!/usr/bin/env python3
"""Verify bilingual artifact outputs and naming policy (T05.2)."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List


NAME_RE = re.compile(r"^.+-ja_ru-\d{8}T\d{6}Z-bilingual\.pdf$")


def _is_pdf(path: Path) -> bool:
    try:
        with path.open("rb") as f:
            return f.read(5) == b"%PDF-"
    except OSError:
        return False


def verify_record(rec: Dict[str, Any]) -> Dict[str, Any]:
    reasons: List[str] = []

    for key in ("run_id", "job_id", "file_id", "output_file"):
        if not rec.get(key):
            reasons.append(f"missing_required_field:{key}")

    output = Path(str(rec.get("output_file", "")))
    if not output.exists():
        reasons.append("output_missing")
    else:
        if output.suffix.lower() != ".pdf":
            reasons.append("output_not_pdf_extension")
        if not _is_pdf(output):
            reasons.append("output_invalid_pdf_header")
        if not NAME_RE.match(output.name):
            reasons.append("output_name_policy_mismatch")

    return {
        "run_id": rec.get("run_id"),
        "job_id": rec.get("job_id"),
        "file_id": rec.get("file_id"),
        "output_file": rec.get("output_file"),
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
    parser = argparse.ArgumentParser(description="Verify bilingual output artifacts")
    parser.add_argument("records", type=Path, help="JSON array with output artifact records")
    parser.add_argument("--output", type=Path, default=Path("logs/artifact-verification.json"))
    args = parser.parse_args()

    records = json.loads(args.records.read_text())
    if isinstance(records, dict):
        records = [records]

    results = [verify_record(r) for r in records]
    summary = summarize(results)
    payload = {"summary": summary, "results": results}

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"status": summary["status"], "failed": summary["failed"], "output": str(args.output)}))
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
