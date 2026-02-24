# OCR Reinsertion Policy (T06.4)

## Goal
Apply translated OCR text back to document visuals while preserving position fidelity.

## Modes
- `replace`: substitute original in-image text when confidence and fit conditions are acceptable.
- `annotation`: keep image unchanged and attach translated text as positioned annotation/overlay anchor.

## Decision rules
Implemented by `scripts/plan_reinsertion.py`:
- use `replace` when:
  - OCR confidence >= `--min-conf-for-replace` (default `0.85`),
  - translated/source length expansion <= `--max-expand-ratio` (default `1.8`),
  - bbox exists (`[x1,y1,x2,y2]`).
- otherwise use `annotation`.

## Output
`reinsertion-plan.json` contains:
- summary counters (`replace`, `annotation`),
- per-segment reinsertion mode,
- fidelity marker (`bbox-aligned` or `anchor-annotation`).

## Example
```bash
python scripts/plan_reinsertion.py translated-segments.json \
  --min-conf-for-replace 0.85 \
  --max-expand-ratio 1.8 \
  --output logs/ocr/reinsertion-plan.json
```
