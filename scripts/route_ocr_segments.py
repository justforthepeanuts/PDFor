#!/usr/bin/env python3
"""Route OCR segments into translation-ready payloads with shared controls (T06.3/T06.5)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def _load(path: Path) -> Any:
    return json.loads(path.read_text())


def _fallback_order(service_cfg: Dict[str, Any], primary: str) -> List[str]:
    order = service_cfg.get("fallback_order", [])
    return [primary] + [s for s in order if s != primary]


def route_segments(
    segments: List[Dict[str, Any]],
    service_cfg: Dict[str, Any],
    run_id: str,
    file_id: str,
    service: str,
    prompt_path: str | None,
    glossary_path: str | None,
    primary_font: str | None,
    low_conf_threshold: float,
) -> Dict[str, Any]:
    payloads: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []

    chain = _fallback_order(service_cfg, service)

    for idx, seg in enumerate(segments, start=1):
        seg_id = seg.get("segment_id") or f"seg_{idx:04d}"
        confidence = float(seg.get("confidence", 1.0))

        payloads.append(
            {
                "run_id": run_id,
                "file_id": file_id,
                "segment_id": seg_id,
                "page": seg.get("page"),
                "bbox": seg.get("bbox"),
                "source_text": seg.get("text", ""),
                "lang_in": "ja",
                "lang_out": "ru",
                "service": service,
                "fallback_order": chain,
                "prompt_path": prompt_path,
                "glossary_path": glossary_path,
                "primary_font": primary_font,
                "translation_controls": {
                    "use_prompt": bool(prompt_path),
                    "use_glossary": bool(glossary_path),
                    "use_font_override": bool(primary_font),
                },
            }
        )

        if confidence < low_conf_threshold:
            warnings.append(
                {
                    "run_id": run_id,
                    "file_id": file_id,
                    "segment_id": seg_id,
                    "page": seg.get("page"),
                    "confidence": confidence,
                    "warning": "low_ocr_confidence",
                    "message": "OCR confidence below threshold; manual review recommended",
                }
            )

    summary = {
        "total_segments": len(payloads),
        "low_confidence_segments": len(warnings),
        "low_conf_threshold": low_conf_threshold,
    }

    return {"summary": summary, "translation_payloads": payloads, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser(description="Route OCR segments into translation payloads")
    parser.add_argument("segments", type=Path, help="OCR segments JSON array")
    parser.add_argument("--services-config", type=Path, default=Path("configs/services.json"))
    parser.add_argument("--run-id", type=str, required=True)
    parser.add_argument("--file-id", type=str, required=True)
    parser.add_argument("--service", type=str, default="openai")
    parser.add_argument("--prompt-path", type=str)
    parser.add_argument("--glossary-path", type=str)
    parser.add_argument("--primary-font", type=str)
    parser.add_argument("--low-conf-threshold", type=float, default=0.80)
    parser.add_argument("--payloads-out", type=Path, default=Path("logs/ocr/translation-payloads.json"))
    parser.add_argument("--warnings-out", type=Path, default=Path("logs/ocr/warnings.json"))
    parser.add_argument("--summary-out", type=Path, default=Path("logs/ocr/summary.json"))
    args = parser.parse_args()

    segments = _load(args.segments)
    if isinstance(segments, dict):
        segments = [segments]
    if not isinstance(segments, list):
        raise ValueError("segments must be a JSON array/object")

    service_cfg = _load(args.services_config)
    flags = service_cfg.get("service_flags", {})
    if args.service not in flags:
        raise ValueError(f"Unsupported service: {args.service}")

    routed = route_segments(
        segments=segments,
        service_cfg=service_cfg,
        run_id=args.run_id,
        file_id=args.file_id,
        service=args.service,
        prompt_path=args.prompt_path,
        glossary_path=args.glossary_path,
        primary_font=args.primary_font,
        low_conf_threshold=args.low_conf_threshold,
    )

    for out, key in [
        (args.payloads_out, "translation_payloads"),
        (args.warnings_out, "warnings"),
        (args.summary_out, "summary"),
    ]:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(routed[key], indent=2) + "\n")

    print(json.dumps({"status": "PASS", "summary": routed["summary"], "warnings_out": str(args.warnings_out)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
