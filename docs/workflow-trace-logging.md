# Workflow Trace Logging (T07.4)

T07.4 adds structured trace logging at workflow branch boundaries to improve observability and incident triage.

## New script

- `scripts/emit_trace_log.py` appends one JSON event per line into `logs/trace/trace.jsonl` (or custom `--log-file`).

Event fields:

- `ts` (UTC ISO timestamp)
- `run_id`
- `trace_id`
- `stage`
- `status`
- optional correlation fields: `job_id`, `file_id`, `page_range`, `details`

## Workflow wiring

Both workflow variants now emit log events at key boundaries:

- after input validation,
- after resilient execution,
- (publication workflow) after output publication.

This ensures each major branch transition has traceable run/trace metadata.

## Example

```bash
python scripts/emit_trace_log.py \
  --run-id run_100 \
  --trace-id trace_100 \
  --stage execute_with_resilience \
  --status ok \
  --log-file logs/trace/trace.jsonl
```
