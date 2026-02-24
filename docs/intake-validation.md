# Intake Schema, Validation & Normalization (T02.1 / T02.2 / T02.3 / T02.4 / T02.5)

## Implemented artifacts
- JSON schema: `configs/input-schema.json`
- Validation script: `scripts/validate_input.py`
- Normalization script: `scripts/normalize_jobs.py`

## Supported payload modes
1. `single`: one input file.
2. `batch`: explicit list of input files.
3. `directory`: directory descriptor that discovers `*.pdf` files (optionally recursive).

## Validation checks
- Required keys by mode.
- Filesystem existence/readability and file type guard.
- Extension check (`.pdf`).
- MIME sanity check (`application/pdf` where available).
- Binary signature check (must begin with `%PDF-`).
- Corrupted/incomplete PDF structure detection (`startxref`/`%%EOF` tail checks).
- Password-protected PDF detection (`/Encrypt` token check).
- Scanned-page heuristic detection (image-dominant + no text blocks) with strict no-proceed policy until OCR preprocessing.

## CLI usage
```bash
python scripts/validate_input.py <payload.json>
python scripts/normalize_jobs.py <payload.json>
```

Exit code behavior for validation:
- `0`: `VALIDATION_OK`
- `1`: `VALIDATION_FAILED` plus list of reasons

Normalization behavior:
- Fails fast if payload validation fails.
- Produces queue-ready job objects including `run_id`, `job_id`, `file_id`, `page_range`, and command-critical parameters.
