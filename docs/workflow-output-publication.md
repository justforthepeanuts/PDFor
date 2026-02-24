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

## Example

```bash
python scripts/publish_outputs.py \
  --artifacts .tmp/artifacts.json \
  --run-id run_123 \
  --publication-mode link \
  --public-base-url https://files.example.local \
  --output .tmp/publication.json
```

Output JSON is suitable for downstream response nodes, webhooks, or simple folder-based consumers.
