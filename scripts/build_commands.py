#!/usr/bin/env python3
"""Build deterministic PDFMathTranslate commands from normalized jobs (T03.1..T03.6)."""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
from pathlib import Path
from typing import Any, Dict, List


OPTIONAL_ARG_ORDER = (
    ("page_range", "--pages", lambda v: v and v != "all"),
    ("pool_max_workers", "--pool-max-workers", lambda v: v is not None),
    ("prompt_path", "--custom-system-prompt", lambda v: bool(v)),
    ("glossary_path", "--glossaries", lambda v: bool(v)),
    ("primary_font", "--primary-font-family", lambda v: bool(v)),
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _service_flag(service: str, config: Dict[str, Any]) -> str | None:
    flags = config.get("service_flags", {})
    if service not in flags:
        raise ValueError(f"Unsupported service '{service}'. Allowed: {sorted(flags)}")
    return flags[service]


def build_argv(job: Dict[str, Any], service_config: Dict[str, Any]) -> List[str]:
    argv: List[str] = [
        "pdf2zh-next",
        str(job["input_file"]),
        "--lang-in",
        str(job.get("lang_in", "ja")),
        "--lang-out",
        str(job.get("lang_out", "ru")),
        "--output",
        str(job["output_dir"]),
    ]

    service = str(job.get("service", "default"))
    flag = _service_flag(service, service_config)
    if flag:
        argv.append(flag)

    for key, flag_name, use in OPTIONAL_ARG_ORDER:
        value = job.get(key)
        if not use(value):
            continue
        if key == "pool_max_workers":
            value = max(1, int(value))
        argv.extend([flag_name, str(value)])

    return argv


def build_records(jobs: List[Dict[str, Any]], service_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for job in jobs:
        argv = build_argv(job, service_config)
        command = shlex.join(argv)
        command_hash = hashlib.sha256(command.encode("utf-8")).hexdigest()
        records.append(
            {
                "run_id": job.get("run_id", "run_local"),
                "job_id": job.get("job_id"),
                "file_id": job.get("file_id"),
                "input_file": job.get("input_file"),
                "page_range": job.get("page_range", "all"),
                "chunked_from": job.get("chunked_from"),
                "service": job.get("service", "default"),
                "fallback_order": service_config.get("fallback_order", []),
                "argv": argv,
                "command": command,
                "command_hash": command_hash,
            }
        )
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description="Build deterministic command(s) from normalized jobs")
    parser.add_argument("jobs", type=Path, help="Path to normalized jobs JSON array")
    parser.add_argument(
        "--service-config",
        type=Path,
        default=Path("configs/services.json"),
        help="Service strategy JSON",
    )
    parser.add_argument("--output", type=Path, help="Where to write command records JSON")
    parser.add_argument("--audit-out", type=Path, help="Write compact audit JSONL")
    args = parser.parse_args()

    jobs = _load_json(args.jobs)
    if isinstance(jobs, dict):
        jobs = [jobs]
    if not isinstance(jobs, list):
        raise ValueError("Expected jobs JSON array or object")

    service_config = _load_json(args.service_config)
    records = build_records(jobs, service_config)

    rendered = json.dumps(records, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n")
    else:
        print(rendered)

    if args.audit_out:
        with args.audit_out.open("w", encoding="utf-8") as f:
            for rec in records:
                compact = {
                    "run_id": rec["run_id"],
                    "job_id": rec["job_id"],
                    "file_id": rec["file_id"],
                    "service": rec["service"],
                    "command_hash": rec["command_hash"],
                    "command": rec["command"],
                }
                f.write(json.dumps(compact, ensure_ascii=False) + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
