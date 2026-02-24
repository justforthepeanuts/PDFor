# Workflow Page-Range Rerun (T07.5)

This workflow variant adds a targeted page-range rerun path before command generation.

## Added artifacts

- `workflow/page-rerun-workflow.json` — n8n workflow variant for partial reruns.
- `scripts/apply_rerun_pages.py` — updates normalized jobs with a specific `page_range`.

## Behavior

1. Validate + normalize input as usual.
2. Apply rerun selection:
   - required `rerun_pages` (for example `5-10`),
   - optional `target_file_id` and/or `target_job_id` to narrow the scope.
3. Build commands from rerun-adjusted jobs (which produces `--pages` flags via command builder).
4. Execute and collect artifacts.

## Example

```bash
python scripts/apply_rerun_pages.py \
  .tmp/jobs.json \
  --pages 5-10 \
  --target-file-id file_001 \
  --output .tmp/jobs-rerun.json
```

The output includes a `rerun` summary object showing how many jobs were adjusted.
