# Acceptance Test Matrix (T08.1)

This matrix maps requirements **R1..R7** to executable scenarios, expected outcomes, and evidence artifacts.

## Matrix

| Requirement | Scenario ID | Scenario | Execution path | Expected result | Evidence artifact(s) |
|---|---|---|---|---|---|
| R1 Input handling | AT-R1-01 | Single valid PDF intake | `validate_input.py` -> `normalize_jobs.py` | Validation passes; one normalized job produced | `logs/test-runs/<run_id>/r1_single_validation.json`, `.../r1_single_jobs.json` |
| R1 Input handling | AT-R1-02 | Batch intake with one invalid file | `validate_input.py` | Invalid entry rejected with explicit failure details | `logs/test-runs/<run_id>/r1_batch_validation.json` |
| R2 Parsing/extraction fidelity | AT-R2-01 | Formula-heavy and table-heavy sample set | `validate_regression_manifest.py` + visual checklist | Samples are registered and evaluated against checklist | `configs/regression-samples.json`, `logs/test-runs/<run_id>/r2_visual_review.md` |
| R3 Translation controls | AT-R3-01 | Service + glossary/prompt controls propagated | `normalize_jobs.py` -> `build_commands.py` | Command record includes selected service and quality flags | `logs/test-runs/<run_id>/r3_command_records.json` |
| R4 Reconstruction/output | AT-R4-01 | Bilingual output verification + page coherence | `verify_bilingual_artifacts.py` + `check_page_coherence.py` | Filename/header and page coherence checks pass | `logs/test-runs/<run_id>/r4_bilingual_check.json`, `.../r4_page_coherence.json` |
| R5 Resilience/fallback | AT-R5-01 | Partial failure continuity with segment reporting | `execute_with_resilience.py` + `format_error_notification.py` | Unaffected jobs continue; failed segments captured; notification severity reflects status | `logs/test-runs/<run_id>/r5_results.json`, `.../r5_segments.json`, `.../r5_notification.json` |
| R6 OCR flow | AT-R6-01 | OCR-required intake routed and reinsertion planned | `ocr_adapter.py` -> `route_ocr_segments.py` -> `plan_reinsertion.py` | OCR route selected; low-confidence warnings surfaced; reinsertion policy produced | `logs/test-runs/<run_id>/r6_ocr_result.json`, `.../r6_warnings.json`, `.../r6_reinsertion_plan.json` |
| R7 Workflow integration | AT-R7-01 | Baseline + retry + publication + rerun variants | `workflow/*.json` + orchestration scripts | Workflow JSON is valid; outputs and rerun path are wired | `logs/test-runs/<run_id>/r7_workflow_validation.txt`, `.../r7_artifacts_manifest.json` |

## Scenario status template

Use this status rubric when executing T08.2/T08.3:

- `PASS`: expected outcomes fully met.
- `FAIL`: required outcome missing or incorrect.
- `WAIVED`: known limitation accepted for release with mitigation.

## Execution record template

For each scenario, store a compact execution record under `logs/test-runs/<run_id>/`:

```json
{
  "scenario_id": "AT-R5-01",
  "status": "PASS",
  "executed_at": "2026-02-24T00:00:00Z",
  "notes": "fallback reached secondary provider after rate-limit",
  "evidence": [
    "logs/test-runs/run_001/r5_results.json",
    "logs/test-runs/run_001/r5_segments.json",
    "logs/test-runs/run_001/r5_notification.json"
  ]
}
```
