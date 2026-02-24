# OCR Decision Tree & Adapter Integration (T06.1 / T06.2)

## T06.1 OCR decision tree
1. Input page/region is analyzed from intake metadata.
2. If scanned/image-dominant heuristic is true:
   - route to OCR preprocessing,
   - set `ocr_required=true`,
   - block direct translation path until OCR artifact exists.
3. If text-native PDF region:
   - skip OCR,
   - continue normal translation extraction.
4. If OCR confidence is low:
   - continue pipeline with warning marker for review (`ocr_warning=true`).

## T06.2 Tool-agnostic OCR adapter
- Script: `scripts/ocr_adapter.py`
- Config: `configs/ocr-tools.json`
- Supported providers (config-driven):
  - `tesseract`
  - `easyocr`
  - `paddleocr`

### Adapter behavior
- Resolves provider command from config templates.
- Supports `--dry-run` for workflow wiring validation without requiring OCR binaries.
- Emits structured JSON with:
  - selected provider,
  - command preview/executed command,
  - output artifact paths,
  - status + error reason.

### Example
```bash
python scripts/ocr_adapter.py sample.png --provider tesseract --dry-run
```


See also: `docs/ocr-translation-routing.md` for T06.3/T06.5 routing and warnings outputs.
