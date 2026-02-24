# Fidelity Checklist & Bilingual Artifact Policy (T05.1 / T05.2)

## T05.1 Measurable fidelity checklist

### Structural fidelity
- Formulas preserved (LaTeX/math tokens not translated): target **0 mistranslated math tokens** in sampled pages.
- Tables preserved: at least **95% cell row/column mapping** retained in sample set.
- Lists preserved: bullet/number markers retained and order unchanged.
- TOC preserved: headings and target page references present.
- Headers/footers/page numbers retained with stable placement.

### Visual/layout fidelity
- No major layout shifts on reference pages (target: <= 5px in visual checks).
- Multi-column reading order remains coherent.
- Figure/text anchoring preserved.

### Artifact-level pass criteria
- Output file exists and is readable as PDF.
- Output naming follows bilingual convention:
  - `<input>-ja_ru-<timestamp>-bilingual.pdf`
- Output page count is coherent with source (equal or documented overflow behavior).

## T05.2 Bilingual artifact policy

### Naming and identity
- Output name suffix MUST include `-bilingual.pdf`.
- Translation direction marker MUST be `ja_ru` for this workflow baseline.
- Timestamp is UTC `YYYYMMDDTHHMMSSZ`.

### Verification hooks
Use `scripts/verify_bilingual_artifacts.py` to perform automated checks:
- file existence and extension,
- `%PDF-` header signature,
- naming convention regex,
- companion metadata integrity (`run_id`, `job_id`, `file_id`, output path),
- aggregated PASS/FAIL summary JSON.

### Evidence output
- Verification summary JSON should be stored in logs (e.g., `logs/artifact-verification.json`).
- Failing files must include explicit reasons for operator rerun decisions.
