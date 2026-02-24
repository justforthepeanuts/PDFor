# OCR Translation Routing & Low-Confidence Warnings (T06.3 / T06.5)

## T06.3 Route OCR text through translation controls
- Script: `scripts/route_ocr_segments.py`
- Input: OCR segment JSON (`segment_id`, `text`, `page`, `bbox`, `confidence`).
- Reuses translation controls aligned with main text path:
  - `service` + `fallback_order` from `configs/services.json`,
  - `prompt_path`,
  - `glossary_path`,
  - `primary_font`.

Output artifacts:
- `translation-payloads.json` — per-segment translation jobs with control metadata.
- `summary.json` — routing totals.

## T06.5 Low-confidence OCR warnings
- Same routing step generates `warnings.json` when confidence is below threshold.
- Default threshold: `0.80` (override via `--low-conf-threshold`).
- Each warning includes segment/page context and review message.

Example:
```bash
python scripts/route_ocr_segments.py ocr-segments.json \
  --run-id run_001 --file-id file_001 \
  --service openai \
  --prompt-path configs/prompt.txt \
  --glossary-path configs/glossary.csv \
  --primary-font "Noto Sans" \
  --low-conf-threshold 0.8
```
