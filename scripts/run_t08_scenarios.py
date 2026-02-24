#!/usr/bin/env python3
"""Execute T08.2 scenario tests and save evidence artifacts."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_cmd(cmd: List[str]) -> Dict[str, Any]:
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def make_pdf(path: Path, scanned: bool = False) -> None:
    if scanned:
        body = b"%PDF-1.4\n1 0 obj<< /Type /Catalog >>endobj\n2 0 obj<< /Subtype /Image >>endobj\nstartxref\n123\n%%EOF\n"
    else:
        body = b"%PDF-1.4\n1 0 obj<< /Type /Catalog /Font <<>> >>endobj\nBT /F1 12 Tf (hello) Tj ET\nstartxref\n123\n%%EOF\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)


def scenario_single(base: Path) -> Dict[str, Any]:
    pdf = base / "inputs/single-ok.pdf"
    make_pdf(pdf)
    payload = {
        "mode": "single",
        "input_file": str(pdf),
        "output_dir": str(base / "out"),
        "run_id": "t08_single",
    }
    payload_path = base / "payload-single.json"
    write_json(payload_path, payload)

    validation = run_cmd(["python", "scripts/validate_input.py", str(payload_path)])
    normalize = run_cmd(["python", "scripts/normalize_jobs.py", str(payload_path), "--output", str(base / "r1_single_jobs.json")])
    write_json(base / "r1_single_validation.json", validation)
    return {
        "scenario_id": "AT-R1-01",
        "status": "PASS" if validation["returncode"] == 0 and normalize["returncode"] == 0 else "FAIL",
        "evidence": ["r1_single_validation.json", "r1_single_jobs.json"],
    }


def scenario_batch_invalid(base: Path) -> Dict[str, Any]:
    valid_pdf = base / "inputs/batch-ok.pdf"
    make_pdf(valid_pdf)
    missing = base / "inputs/missing.pdf"
    payload = {
        "mode": "batch",
        "input_files": [str(valid_pdf), str(missing)],
        "output_dir": str(base / "out"),
        "run_id": "t08_batch",
    }
    payload_path = base / "payload-batch-invalid.json"
    write_json(payload_path, payload)
    validation = run_cmd(["python", "scripts/validate_input.py", str(payload_path)])
    write_json(base / "r1_batch_validation.json", validation)
    failed_as_expected = validation["returncode"] != 0 and "File not found" in validation["stdout"]
    return {
        "scenario_id": "AT-R1-02",
        "status": "PASS" if failed_as_expected else "FAIL",
        "evidence": ["r1_batch_validation.json"],
    }


def scenario_scanned_warning(base: Path) -> Dict[str, Any]:
    scanned_pdf = base / "inputs/scanned.pdf"
    make_pdf(scanned_pdf, scanned=True)
    payload = {
        "mode": "single",
        "input_file": str(scanned_pdf),
        "output_dir": str(base / "out"),
        "run_id": "t08_scanned",
    }
    payload_path = base / "payload-scanned.json"
    write_json(payload_path, payload)
    validation = run_cmd(["python", "scripts/validate_input.py", str(payload_path)])
    write_json(base / "r_scanned_validation.json", validation)
    triggered = validation["returncode"] != 0 and "pre-OCR is required" in validation["stdout"]
    return {
        "scenario_id": "AT-R6-01",
        "status": "PASS" if triggered else "FAIL",
        "evidence": ["r_scanned_validation.json"],
    }


def scenario_large_file_chunking(base: Path) -> Dict[str, Any]:
    jobs = [
        {"run_id": "t08_large", "job_id": "job_0001", "file_id": "file_large", "input_file": "large.pdf", "output_dir": "out", "lang_in": "ja", "lang_out": "ru", "service": "default", "page_range": "all"}
    ]
    write_json(base / "jobs-large.json", jobs)
    write_json(base / "page-counts.json", {"file_large": 120})
    chunk = run_cmd([
        "python", "scripts/plan_page_chunks.py", str(base / "jobs-large.json"), "--page-counts", str(base / "page-counts.json"), "--max-pages-per-part", "50", "--output", str(base / "r_large_chunked.json")
    ])
    write_json(base / "r_large_chunking_cmd.json", chunk)
    chunked = json.loads((base / "r_large_chunked.json").read_text())
    ok = len(chunked) == 3
    return {"scenario_id": "AT-R5-LARGE", "status": "PASS" if ok and chunk["returncode"] == 0 else "FAIL", "evidence": ["r_large_chunked.json"]}


def scenario_rate_limit_partial(base: Path) -> Dict[str, Any]:
    records = [
        {"run_id": "t08_res", "job_id": "job_ok", "file_id": "f_ok", "input_file": "ok.pdf", "page_range": "1-1", "service": "default", "argv": ["python", "-c", "print('ok')"]},
        {"run_id": "t08_res", "job_id": "job_fail", "file_id": "f_fail", "input_file": "fail.pdf", "page_range": "2-3", "service": "default", "argv": ["python", "-c", "import sys;sys.stderr.write('429 rate limit');sys.exit(75)"]}
    ]
    svc = {"service_flags": {"default": None}, "fallback_order": []}
    write_json(base / "records.json", records)
    write_json(base / "services.json", svc)

    exec_res = run_cmd([
        "python", "scripts/execute_with_resilience.py", str(base / "records.json"), "--service-config", str(base / "services.json"), "--output", str(base / "r5_results.json"), "--segments-out", str(base / "r5_segments.json"), "--summary-out", str(base / "r5_summary.json"), "--max-attempts", "2", "--base-delay-s", "0.01", "--max-workers", "2"
    ])
    write_json(base / "r5_exec_cmd.json", exec_res)
    notif = run_cmd([
        "python", "scripts/format_error_notification.py", "--summary", str(base / "r5_summary.json"), "--segments", str(base / "r5_segments.json"), "--run-id", "t08_res", "--output", str(base / "r5_notification.json")
    ])
    write_json(base / "r5_notification_cmd.json", notif)
    summary = json.loads((base / "r5_summary.json").read_text())
    ok = summary.get("total") == 2 and summary.get("failed") == 1 and summary.get("partial_failure") is True
    return {"scenario_id": "AT-R5-01", "status": "PASS" if ok else "FAIL", "evidence": ["r5_results.json", "r5_segments.json", "r5_summary.json", "r5_notification.json"]}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run T08.2 scenario tests")
    parser.add_argument("--run-id", default="run_t08_001")
    args = parser.parse_args()

    base = Path("logs/test-runs") / args.run_id
    base.mkdir(parents=True, exist_ok=True)

    scenarios = [
        scenario_single(base),
        scenario_batch_invalid(base),
        scenario_scanned_warning(base),
        scenario_large_file_chunking(base),
        scenario_rate_limit_partial(base),
    ]
    summary = {
        "run_id": args.run_id,
        "total": len(scenarios),
        "passed": sum(1 for s in scenarios if s["status"] == "PASS"),
        "failed": sum(1 for s in scenarios if s["status"] != "PASS"),
        "scenarios": scenarios,
    }
    write_json(base / "t08.2-summary.json", summary)
    print(json.dumps(summary))
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
