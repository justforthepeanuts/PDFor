#!/usr/bin/env python3
"""Execute command records with retry/backoff and service fallback (T04.2/T04.3)."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List


RETRYABLE_EXIT_CODES = {75}


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


def execute_records(
    records: List[Dict[str, Any]],
    service_config: Dict[str, Any],
    max_attempts: int,
    base_delay_s: float,
    dry_run: bool,
) -> List[Dict[str, Any]]:
    flags = service_config.get("service_flags", {})
    fallback_order = service_config.get("fallback_order", [])

    results: List[Dict[str, Any]] = []
    for rec in records:
        result = {
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
                    rc, stdout, stderr = 0, "", ""
                else:
                    proc = _run(argv)
                    rc, stdout, stderr = proc.returncode, proc.stdout, proc.stderr

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
                    results.append(result)
                    break

                err_class = classify_error(rc, stderr)
                attempt_row["error_class"] = err_class
                attempt_row["stderr"] = stderr[-500:]
                result["attempts"].append(attempt_row)

                retryable = err_class in {"api_rate_limit", "transient_network"}
                if retryable and attempt < max_attempts:
                    time.sleep(base_delay_s * (2 ** (attempt - 1)))
                    continue
                break

            if result["status"] == "success":
                break

        if result["status"] != "success":
            last = result["attempts"][-1] if result["attempts"] else {}
            result["failure_reason"] = last.get("error_class", "unknown")
            result["final_service"] = last.get("service", base_service)
            results.append(result)

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute command records with resilience policies")
    parser.add_argument("records", type=Path, help="Command records JSON from build_commands.py")
    parser.add_argument("--service-config", type=Path, default=Path("configs/services.json"))
    parser.add_argument("--output", type=Path, default=Path("logs/execution-results.json"))
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--base-delay-s", type=float, default=0.1)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    records = json.loads(args.records.read_text())
    if isinstance(records, dict):
        records = [records]

    service_config = json.loads(args.service_config.read_text())
    results = execute_records(records, service_config, args.max_attempts, args.base_delay_s, args.dry_run)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2) + "\n")

    failed = sum(1 for r in results if r["status"] != "success")
    print(json.dumps({"total": len(results), "failed": failed, "output": str(args.output)}))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
