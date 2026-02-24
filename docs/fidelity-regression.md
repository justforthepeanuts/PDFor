# Overflow Coherence & Regression Samples (T05.3 / T05.4)

## T05.3 Overflow/page-coherence checks
- Script: `scripts/check_page_coherence.py`
- Input: JSON array of records with `source_pages`, `output_pages`, and overflow annotations.
- Pass logic:
  - output pages must not be less than source pages,
  - when page counts differ, overflow policy must be explicit and reported.

Example:
```bash
python scripts/check_page_coherence.py records.json --output logs/page-coherence.json
```

## T05.4 Regression samples for fidelity stress cases
- Manifest: `configs/regression-samples.json`
- Manifest validator: `scripts/validate_regression_manifest.py`
- Required categories include table-heavy/formula-heavy/multi-column variants.

Example:
```bash
python scripts/validate_regression_manifest.py configs/regression-samples.json
```
