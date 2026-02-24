#!/usr/bin/env python3
"""Plan OCR text reinsertion strategy: replace vs annotation (T06.4)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def decide_mode(seg: Dict[str, Any], min_conf: float, max_expand_ratio: float) -> str:
    confidence = float(seg.get("confidence", 0.0))
    source_len = max(1, len(str(seg.get("source_text", ""))))
    translated_len = len(str(seg.get("translated_text", "")))
    expansion = translated_len / source_len
    bbox = seg.get("bbox") or []
    bbox_ok = isinstance(bbox, list) and len(bbox) == 4

    if confidence >= min_conf and expansion <= max_expand_ratio and bbox_ok:
        return "replace"
    return "annotation"


def plan_reinsertion(
    segments: List[Dict[str, Any]],
    min_conf: float,
    max_expand_ratio: float,
) -> Dict[str, Any]:
    plans: List[Dict[str, Any]] = []
    replace_count = 0
    annotation_count = 0

    for idx, seg in enumerate(segments, start=1):
        segment_id = seg.get("segment_id") or f"seg_{idx:04d}"
        mode = decide_mode(seg, min_conf=min_conf, max_expand_ratio=max_expand_ratio)
        if mode == "replace":
            replace_count += 1
        else:
            annotation_count += 1

        plans.append(
            {
                "segment_id": segment_id,
                "page": seg.get("page"),
                "bbox": seg.get("bbox"),
                "mode": mode,
                "position_fidelity": "bbox-aligned" if mode == "replace" else "anchor-annotation",
                "translated_text": seg.get("translated_text", ""),
                "confidence": seg.get("confidence"),
            }
        )

    return {
        "summary": {
            "total_segments": len(segments),
            "replace": replace_count,
            "annotation": annotation_count,
            "min_conf_for_replace": min_conf,
            "max_expand_ratio_for_replace": max_expand_ratio,
        },
        "plans": plans,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan reinsertion mode for OCR translated segments")
    parser.add_argument("segments", type=Path, help="JSON array of translated OCR segments")
    parser.add_argument("--min-conf-for-replace", type=float, default=0.85)
    parser.add_argument("--max-expand-ratio", type=float, default=1.8)
    parser.add_argument("--output", type=Path, default=Path("logs/ocr/reinsertion-plan.json"))
    args = parser.parse_args()

    segments = json.loads(args.segments.read_text())
    if isinstance(segments, dict):
        segments = [segments]
    if not isinstance(segments, list):
        raise ValueError("segments must be JSON array/object")

    result = plan_reinsertion(
        segments,
        min_conf=args.min_conf_for_replace,
        max_expand_ratio=args.max_expand_ratio,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "summary": result["summary"], "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
