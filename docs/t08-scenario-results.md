# T08.2 Scenario Test Execution Results

Run ID: `run_t08_001`

## Executed scenarios

| Scenario | Description | Status | Evidence |
|---|---|---|---|
| AT-R1-01 | single file intake | PASS | `logs/test-runs/run_t08_001/r1_single_validation.json`, `.../r1_single_jobs.json` |
| AT-R1-02 | batch intake with invalid file | PASS | `logs/test-runs/run_t08_001/r1_batch_validation.json` |
| AT-R6-01 | scanned warning / OCR-required routing gate | PASS | `logs/test-runs/run_t08_001/r_scanned_validation.json` |
| AT-R5-LARGE | large file chunking safeguard | PASS | `logs/test-runs/run_t08_001/r_large_chunked.json` |
| AT-R5-01 | rate-limit retry + partial failure continuity + notification | PASS | `logs/test-runs/run_t08_001/r5_results.json`, `.../r5_segments.json`, `.../r5_summary.json`, `.../r5_notification.json` |

## Summary

- Total: 5
- Passed: 5
- Failed: 0

Machine-readable run summary: `logs/test-runs/run_t08_001/t08.2-summary.json`.
