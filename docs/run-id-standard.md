# Run Correlation Standard

Every workflow execution must include the following IDs across logs, payloads, and artifacts metadata:

- `run_id`: unique identifier for the workflow execution.
- `job_id`: unique identifier per normalized job payload.
- `file_id`: stable identifier for each input file in job scope.
- `page_range`: translated page subset (`all` or explicit range string such as `1,3,5-7`).

## Log envelope (minimum)
```json
{
  "run_id": "run_20260224_0001",
  "job_id": "job_01",
  "file_id": "sha256:...",
  "page_range": "all",
  "status": "started"
}
```
