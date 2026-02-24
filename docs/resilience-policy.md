# Resilience & Fallback Policy (T04.1..T04.5)

## Error taxonomy (T04.1)
- `validation_error`: malformed payload, missing files, unsupported options.
- `api_rate_limit`: provider throttling / quota responses.
- `transient_network`: temporary connectivity/DNS/timeouts.
- `oom_or_resource`: memory/CPU pressure, worker crashes.
- `file_level_failure`: one file/page fails while others are still processable.

## Retry policy (T04.2)
- Retry only for transient classes: `api_rate_limit`, `transient_network`, selected non-deterministic runtime failures.
- Default `max_attempts`: 3 per service.
- Default backoff: exponential (`base_delay_s * 2^(attempt-1)`) with optional jitter.
- Stop early on non-retryable classes (`validation_error`, deterministic argument errors).

## Service fallback policy (T04.3)
- Primary service is attempted first (from command record).
- On retry exhaustion for retryable errors, switch to next service from configured `fallback_order`.
- Preserve progress by recording per-job state after each attempt and continuing to the next job regardless of previous job failure.
- Output result includes: attempts, service transitions, final status, and failure reason.

## Large-file safeguards (T04.4)
- Chunking utility: `scripts/plan_page_chunks.py` splits `all` page jobs into bounded ranges (`--max-pages-per-part`, default 50).
- Worker caps: `scripts/execute_with_resilience.py --max-workers <N>` limits concurrent job execution.

## Atomic output safety (T04.5)
- Execution results are written via temporary file + atomic replace in `atomic_write_json(...)`.
- Guarantees no half-written JSON result file on interruption at write time.
