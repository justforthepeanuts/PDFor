#!/usr/bin/env python3
"""Normalize validated intake payload into queue-ready job envelopes (T02.5)."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

from validate_input import collect_files, validate_payload


def _file_id(path: Path) -> str:
    digest = hashlib.sha256(str(path).encode("utf-8")).hexdigest()[:16]
    return f"file_{digest}"


def normalize(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    result = validate_payload(payload)
    if result["errors"]:
        raise ValueError("Payload validation failed; refusing to normalize")

    files = collect_files(payload)
    run_id = payload.get("run_id", "run_local")
    output_dir = payload["output_dir"]
    page_range = payload.get("page_range", "all")
    service = payload.get("service", "default")

    jobs: List[Dict[str, Any]] = []
    for idx, file_path in enumerate(files, start=1):
        jobs.append(
            {
                "run_id": run_id,
                "job_id": f"job_{idx:04d}",
                "file_id": _file_id(file_path),
                "input_file": str(file_path),
                "output_dir": output_dir,
                "lang_in": "ja",
                "lang_out": "ru",
                "service": service,
                "page_range": page_range,
                "pool_max_workers": payload.get("pool_max_workers", 2),
            }
        )
    return jobs


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize intake payload into queue jobs.")
    parser.add_argument("payload", type=Path, help="Path to intake payload JSON")
    parser.add_argument("--output", type=Path, help="Optional path to save normalized JSON")
    args = parser.parse_args()

    payload = json.loads(args.payload.read_text())
    jobs = normalize(payload)

    rendered = json.dumps(jobs, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n")
    else:
        print(rendered)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
