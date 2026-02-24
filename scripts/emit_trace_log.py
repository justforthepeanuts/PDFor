#!/usr/bin/env python3
"""Emit structured trace logs for workflow branch boundaries."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit a structured trace log event")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--trace-id", required=True)
    parser.add_argument("--stage", required=True)
    parser.add_argument("--status", default="ok")
    parser.add_argument("--job-id")
    parser.add_argument("--file-id")
    parser.add_argument("--page-range")
    parser.add_argument("--details")
    parser.add_argument("--log-file", default="logs/trace/trace.jsonl")
    args = parser.parse_args()

    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "run_id": args.run_id,
        "trace_id": args.trace_id,
        "stage": args.stage,
        "status": args.status,
    }
    if args.job_id:
        event["job_id"] = args.job_id
    if args.file_id:
        event["file_id"] = args.file_id
    if args.page_range:
        event["page_range"] = args.page_range
    if args.details:
        event["details"] = args.details

    log_path = Path(args.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")

    print("TRACE_LOGGED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
