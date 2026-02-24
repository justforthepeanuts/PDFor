#!/usr/bin/env python3
"""Apply a targeted page range to normalized jobs for rerun flows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _matches_target(job: Dict[str, Any], target_file_id: str | None, target_job_id: str | None) -> bool:
    if target_file_id and job.get("file_id") != target_file_id:
        return False
    if target_job_id and job.get("job_id") != target_job_id:
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply rerun page range to normalized jobs")
    parser.add_argument("jobs", help="Input normalized jobs JSON")
    parser.add_argument("--pages", required=True, help="Page range to apply, e.g. 5-10")
    parser.add_argument("--target-file-id", help="Optional file_id filter")
    parser.add_argument("--target-job-id", help="Optional job_id filter")
    parser.add_argument("--output", required=True, help="Output jobs JSON path")
    args = parser.parse_args()

    payload = _read_json(Path(args.jobs))
    jobs: List[Dict[str, Any]] = payload.get("jobs", [])

    updated = 0
    for job in jobs:
        if _matches_target(job, args.target_file_id, args.target_job_id):
            job["page_range"] = args.pages
            job["rerun"] = True
            updated += 1

    payload["rerun"] = {
        "pages": args.pages,
        "target_file_id": args.target_file_id,
        "target_job_id": args.target_job_id,
        "updated_jobs": updated,
    }

    _write_json(Path(args.output), payload)
    print("RERUN_PAGES_APPLIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
