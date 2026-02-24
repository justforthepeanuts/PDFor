#!/usr/bin/env python3
"""Build standardized workflow notifications from execution outputs (T07.2)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def _load(path: Path) -> Any:
    return json.loads(path.read_text())


def build_notification(summary: Dict[str, Any], segments: List[Dict[str, Any]], run_id: str | None) -> Dict[str, Any]:
    failed = int(summary.get("failed", 0))
    total = int(summary.get("total", 0))
    success = int(summary.get("success", max(0, total - failed)))

    if failed == 0:
        severity = "INFO"
        status = "SUCCESS"
        message = f"Run {run_id or 'unknown'} completed successfully: {success}/{total} jobs passed."
    elif failed < total:
        severity = "WARN"
        status = "PARTIAL_FAILURE"
        message = (
            f"Run {run_id or 'unknown'} completed with partial failures: "
            f"{success}/{total} passed, {failed} failed."
        )
    else:
        severity = "ERROR"
        status = "FAILED"
        message = f"Run {run_id or 'unknown'} failed: {failed}/{total} jobs failed."

    top_segments = []
    if failed > 0:
        for seg in segments[:10]:
            top_segments.append(
                {
                    "job_id": seg.get("job_id"),
                    "file_id": seg.get("file_id"),
                    "page_range": seg.get("page_range"),
                    "failure_reason": seg.get("failure_reason"),
                }
            )

    return {
        "run_id": run_id,
        "status": status,
        "severity": severity,
        "message": message,
        "summary": {
            "total": total,
            "success": success,
            "failed": failed,
            "partial_failure": bool(summary.get("partial_failure", failed > 0 and failed < total)),
        },
        "problem_segments": top_segments,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Format standardized error notification JSON")
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--segments", type=Path, required=True)
    parser.add_argument("--run-id", type=str)
    parser.add_argument("--output", type=Path, default=Path("logs/notifications/latest.json"))
    args = parser.parse_args()

    summary = _load(args.summary)
    segments = _load(args.segments)
    if isinstance(segments, dict):
        segments = [segments]

    payload = build_notification(summary=summary, segments=segments, run_id=args.run_id)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"status": payload["status"], "severity": payload["severity"], "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
