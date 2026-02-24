#!/usr/bin/env python3
"""Execute command records with retry/backoff and service fallback (T04.2/T04.6)."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Tuple


RETRYABLE_EXIT_CODES = {75}
RETRYABLE_CLASSES = {"api_rate_limit", "transient_network"}


def classify_error(exit_code: int, stderr: str) -> str:
    text = (stderr or "").lower()
    if "rate limit" in text or "429" in text:
        return "api_rate_limit"
    if "timeout" in text or "temporary failure" in text or "network" in text:
        return "transient_network"
    if "memory" in text or "oom" in text:
        return "oom_or_resource"
    if "invalid" in text or "missing" in text:
        return "validation_error"
    if exit_code in RETRYABLE_EXIT_CODES:
        return "transient_network"
    return "file_level_failure"


def _replace_service_flag(argv: List[str], old: str | None, new: str | None) -> List[str]:
    out = [p for p in argv if p != old] if old else list(argv)
    if new:
        insert_at = 8 if len(out) >= 8 else len(out)
        out.insert(insert_at, new)
    return out


def _command_from_argv(argv: List[str]) -> str:
    return subprocess.list2cmdline(argv)


def _run(argv: List[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, capture_output=True, text=True, check=False)


def _execute_one_record(
    rec: Dict[str, Any],
    service_config: Dict[str, Any],
    max_attempts: int,
    base_delay_s: float,
    dry_run: bool,
) -> Dict[str, Any]:
    flags = service_config.get("service_flags", {})
    fallback_order = service_config.get("fallback_order", [])

    result: Dict[str, Any] = {
        "run_id": rec.get("run_id"),
        "job_id": rec.get("job_id"),
        "file_id": rec.get("file_id"),
        "attempts": [],
        "status": "failed",
    }

    base_service = rec.get("service", "default")
    chain = [base_service] + [s for s in fallback_order if s != base_service]

    for service in chain:
        service_flag = flags.get(service)
        old_flag = flags.get(base_service)
        argv = _replace_service_flag(rec["argv"], old_flag, service_flag)
        command = _command_from_argv(argv)

        for attempt in range(1, max_attempts + 1):
            if dry_run:
                rc, stderr = 0, ""
            else:
                proc = _run(argv)
                rc, stderr = proc.returncode, proc.stderr

            attempt_row = {
                "service": service,
                "attempt": attempt,
                "returncode": rc,
                "error_class": None,
                "command": command,
            }

            if rc == 0:
                result["attempts"].append(attempt_row)
                result["status"] = "success"
                result["final_service"] = service
                return result

            err_class = classify_error(rc, stderr)
            attempt_row["error_class"] = err_class
            attempt_row["stderr"] = stderr[-500:]
            result["attempts"].append(attempt_row)

            if err_class in RETRYABLE_CLASSES and attempt < max_attempts:
                time.sleep(base_delay_s * (2 ** (attempt - 1)))
                continue
            break

    last = result["attempts"][-1] if result["attempts"] else {}
    result["failure_reason"] = last.get("error_class", "unknown")
    result["final_service"] = last.get("service", base_service)
    return result


def execute_records(
    records: List[Dict[str, Any]],
    service_config: Dict[str, Any],
    max_attempts: int,
    base_delay_s: float,
    dry_run: bool,
    max_workers: int,
) -> List[Dict[str, Any]]:
    if max_workers <= 1:
        return [
            _execute_one_record(rec, service_config, max_attempts, base_delay_s, dry_run)
            for rec in records
        ]

    indexed: List[Tuple[int, Dict[str, Any]]] = list(enumerate(records))
    by_idx: Dict[int, Dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(_execute_one_record, rec, service_config, max_attempts, base_delay_s, dry_run): idx
            for idx, rec in indexed
        }
        for fut in as_completed(futures):
            by_idx[futures[fut]] = fut.result()

    return [by_idx[i] for i in range(len(records))]


def atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent) as tmp:
        tmp.write(json.dumps(payload, indent=2) + "\n")
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute command records with resilience policies")
    parser.add_argument("records", type=Path, help="Command records JSON from build_commands.py")
    parser.add_argument("--service-config", type=Path, default=Path("configs/services.json"))
    parser.add_argument("--output", type=Path, default=Path("logs/execution-results.json"))
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--base-delay-s", type=float, default=0.1)
    parser.add_argument("--max-workers", type=int, default=2)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    records = json.loads(args.records.read_text())
    if isinstance(records, dict):
        records = [records]

    service_config = json.loads(args.service_config.read_text())
    results = execute_records(
        records,
        service_config,
        max_attempts=max(1, args.max_attempts),
        base_delay_s=max(0.0, args.base_delay_s),
        dry_run=args.dry_run,
        max_workers=max(1, args.max_workers),
    )

    atomic_write_json(args.output, results)

    failed = sum(1 for r in results if r["status"] != "success")
    print(json.dumps({"total": len(results), "failed": failed, "output": str(args.output)}))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
