#!/usr/bin/env python3
"""Intake payload and PDF file validation for PDFinator (T02.1..T02.4)."""

from __future__ import annotations

import argparse
import json
import mimetypes
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


def _read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def _is_pdf_header(raw: bytes) -> bool:
    return raw.startswith(b"%PDF-")


def _has_eof_marker(raw: bytes) -> bool:
    tail = raw[-2048:] if len(raw) > 2048 else raw
    return b"%%EOF" in tail and b"startxref" in tail


def _is_password_protected(raw: bytes) -> bool:
    return b"/Encrypt" in raw


def _scan_heuristic(raw: bytes) -> bool:
    """True when PDF appears image-dominant and text-poor (likely scanned)."""
    images = raw.count(b"/Subtype /Image") + raw.count(b"/Image")
    text_blocks = raw.count(b"BT")
    fonts = raw.count(b"/Font")
    return images > 0 and text_blocks == 0 and fonts <= 1


def _validate_file(path: Path) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    if not path.exists():
        return [f"File not found: {path}"], warnings
    if not path.is_file():
        return [f"Not a file: {path}"], warnings
    if path.suffix.lower() != ".pdf":
        return [f"Invalid extension (expected .pdf): {path}"], warnings

    guessed_mime, _ = mimetypes.guess_type(str(path))
    if guessed_mime not in (None, "application/pdf"):
        return [f"Invalid MIME type {guessed_mime!r} for file: {path}"], warnings

    try:
        raw = _read_bytes(path)
    except OSError as exc:
        return [f"Unreadable file {path}: {exc}"], warnings

    if not _is_pdf_header(raw):
        errors.append(f"Invalid PDF header in file: {path}")
    if not _has_eof_marker(raw):
        errors.append(f"Corrupted or incomplete PDF structure detected (missing EOF/xref): {path}")
    if _is_password_protected(raw):
        errors.append(f"Password-protected PDF detected and cannot be processed: {path}")
    if _scan_heuristic(raw):
        warnings.append(
            f"Scanned-page heuristic triggered for {path}; pre-OCR is required before translation"
        )

    return errors, warnings


def collect_files(payload: dict) -> List[Path]:
    mode = payload["mode"]
    if mode == "single":
        return [Path(payload["input_file"])]
    if mode == "batch":
        return [Path(p) for p in payload["input_files"]]
    if mode == "directory":
        input_dir = Path(payload["input_dir"])
        recursive = bool(payload.get("recursive", False))
        pattern = "**/*.pdf" if recursive else "*.pdf"
        return sorted(input_dir.glob(pattern))
    raise ValueError(f"Unsupported mode: {mode}")


def validate_payload(payload: dict) -> Dict[str, List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    required_by_mode = {
        "single": {"mode", "input_file", "output_dir"},
        "batch": {"mode", "input_files", "output_dir"},
        "directory": {"mode", "input_dir", "output_dir"},
    }

    mode = payload.get("mode")
    if mode not in required_by_mode:
        return {"errors": ["Invalid mode; expected one of: single, batch, directory"], "warnings": []}

    missing = required_by_mode[mode] - set(payload.keys())
    if missing:
        errors.append(f"Missing required keys for mode={mode}: {sorted(missing)}")

    try:
        files = collect_files(payload)
    except Exception as exc:
        return {"errors": [f"Failed to resolve files from payload: {exc}"], "warnings": []}

    if mode == "directory" and not files:
        errors.append(f"No PDF files found in directory: {payload.get('input_dir')}")

    for path in files:
        e, w = _validate_file(path)
        errors.extend(e)
        warnings.extend(w)

    # strict policy per requirements: scanned docs must not proceed without OCR
    for w in warnings:
        if "pre-OCR is required" in w:
            errors.append(w)

    return {"errors": errors, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate intake payload and PDF files.")
    parser.add_argument("payload", type=Path, help="Path to JSON payload file")
    args = parser.parse_args()

    payload = json.loads(args.payload.read_text())
    result = validate_payload(payload)
    errors = result["errors"]
    warnings = result["warnings"]

    if errors:
        print("VALIDATION_FAILED")
        for err in errors:
            print(f"- {err}")
        return 1

    for warn in warnings:
        print(f"WARN: {warn}")
    print("VALIDATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
