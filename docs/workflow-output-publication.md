# Workflow Output Publication (T07.3)

This workflow increment adds publication nodes so each run can finish with one of three delivery modes:

- direct file links,
- API response payload,
- folder handoff contract.

## Added artifacts

- `workflow/publication-workflow.json` — n8n flow variant with publication stage.
- `scripts/publish_outputs.py` — converts collected artifact paths into a publication payload.

## Publication modes

`publish_outputs.py` accepts `--publication-mode` with these values:

- `link`: returns a `direct_link` delivery object with URL(s) built from `--public-base-url`.
- `api`: returns an `api_response` delivery object with endpoint + payload contract.
- `folder`: returns a `folder_handoff` delivery object with handoff directory and file list.

## Input options

The publisher supports both input styles:

- `--artifacts <json-file>` to read a collected-artifacts map.
- direct path flags (`--results-path`, `--summary-path`, `--notification-path`) when no artifacts file is present.

This keeps the workflow resilient even when an artifacts manifest file is not materialized.

## Example

```bash
python scripts/publish_outputs.py \
  --run-id run_123 \
  --publication-mode link \
  --public-base-url https://files.example.local \
  --results-path logs/runs/run_123/results.json \
  --summary-path logs/runs/run_123/summary.json \
  --notification-path logs/notifications/run_123.json \
  --output .tmp/publication.json
```

Output JSON is suitable for downstream response nodes, webhooks, or simple folder-based consumers.
