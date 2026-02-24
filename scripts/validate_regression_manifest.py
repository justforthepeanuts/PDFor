#!/usr/bin/env python3
"""Validate regression sample manifest for fidelity suites (T05.4)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


REQUIRED_KEYS = {"sample_id", "category", "input_file", "expected_checks"}


def validate_entry(entry: Dict[str, Any]) -> List[str]:
    errs: List[str] = []
    missing = REQUIRED_KEYS - set(entry)
    if missing:
        errs.append(f"missing_keys:{sorted(missing)}")

    if not isinstance(entry.get("sample_id"), str) or not entry.get("sample_id"):
        errs.append("invalid_sample_id")
    if not isinstance(entry.get("category"), str) or not entry.get("category"):
        errs.append("invalid_category")
    if not isinstance(entry.get("input_file"), str) or not entry.get("input_file", "").endswith(".pdf"):
        errs.append("invalid_input_file")
    checks = entry.get("expected_checks")
    if not isinstance(checks, list) or not checks or not all(isinstance(x, str) for x in checks):
        errs.append("invalid_expected_checks")
    return errs


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate regression sample manifest")
    parser.add_argument("manifest", type=Path, help="Path to regression manifest JSON")
    args = parser.parse_args()

    data = json.loads(args.manifest.read_text())
    if not isinstance(data, list):
        print("MANIFEST_INVALID:root_not_array")
        return 1

    all_errors: List[str] = []
    ids = set()
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            all_errors.append(f"entry[{i}]:not_object")
            continue
        entry_errors = validate_entry(entry)
        all_errors.extend([f"entry[{i}]:{e}" for e in entry_errors])
        sid = entry.get("sample_id")
        if sid in ids:
            all_errors.append(f"entry[{i}]:duplicate_sample_id:{sid}")
        ids.add(sid)

    if all_errors:
        print("MANIFEST_INVALID")
        for err in all_errors:
            print(f"- {err}")
        return 1

    print(f"MANIFEST_OK:count={len(data)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
