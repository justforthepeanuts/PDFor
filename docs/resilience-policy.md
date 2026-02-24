# Resilience & Fallback Policy (T04.1..T04.3)

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
