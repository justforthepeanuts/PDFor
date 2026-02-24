# Retry/Fallback Branching + Standardized Notifications (T07.2)

Implemented artifacts:
- `workflow/retry-fallback-workflow.json`
- `scripts/format_error_notification.py`

## What is added beyond baseline
- Keeps resilient execution in the graph (`scripts/execute_with_resilience.py`).
- Adds explicit standardized notification formatting node after execution.
- Produces notification JSON with severity/status classes:
  - `INFO` / `SUCCESS`
  - `WARN` / `PARTIAL_FAILURE`
  - `ERROR` / `FAILED`

## Notification payload includes
- run-level summary (`total`, `success`, `failed`, `partial_failure`)
- concise human-readable message
- top failed problem segments (`job_id`, `file_id`, `page_range`, `failure_reason`)

## Example utility run
```bash
python scripts/format_error_notification.py \
  --summary logs/execution-summary.json \
  --segments logs/problem-segments.json \
  --run-id run_001 \
  --output logs/notifications/latest.json
```
