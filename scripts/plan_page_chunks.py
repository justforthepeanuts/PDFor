#!/usr/bin/env python3
"""Expand normalized jobs into chunked page ranges for large-file safeguards (T04.4)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def _chunks(total_pages: int, max_pages_per_part: int) -> List[str]:
    ranges: List[str] = []
    start = 1
    while start <= total_pages:
        end = min(total_pages, start + max_pages_per_part - 1)
        ranges.append(f"{start}-{end}")
        start = end + 1
    return ranges


def expand_jobs(
    jobs: List[Dict[str, Any]], page_counts: Dict[str, int], max_pages_per_part: int
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for job in jobs:
        if job.get("page_range") not in (None, "all"):
            out.append(job)
            continue

        key = job.get("file_id") or str(job.get("input_file"))
        page_count = page_counts.get(key)
        if not page_count or page_count <= max_pages_per_part:
            out.append(job)
            continue

        for idx, page_range in enumerate(_chunks(page_count, max_pages_per_part), start=1):
            clone = dict(job)
            clone["job_id"] = f"{job['job_id']}_part{idx:02d}"
            clone["page_range"] = page_range
            clone["chunked_from"] = job["job_id"]
            out.append(clone)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan page-range chunks for large files")
    parser.add_argument("jobs", type=Path, help="Normalized jobs JSON")
    parser.add_argument("--page-counts", type=Path, required=True, help="JSON map of file_id/path -> page count")
    parser.add_argument("--max-pages-per-part", type=int, default=50)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    jobs = json.loads(args.jobs.read_text())
    page_counts = json.loads(args.page_counts.read_text())

    planned = expand_jobs(jobs, page_counts, max(1, args.max_pages_per_part))
    args.output.write_text(json.dumps(planned, indent=2) + "\n")
    print(json.dumps({"input_jobs": len(jobs), "output_jobs": len(planned), "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
