# Production Readiness Checklist, Known Limitations, and Mitigations (T08.4)

This document consolidates readiness status after T08.1–T08.3 execution artifacts.

## 1) Release readiness checklist

| Area | Check | Status | Evidence |
|---|---|---|---|
| Intake validation | Single/batch input validation with explicit failures | PASS | `logs/test-runs/run_t08_001/r1_single_validation.json`, `r1_batch_validation.json` |
| OCR gate | Scanned-file detection blocks non-OCR path | PASS | `logs/test-runs/run_t08_001/r_scanned_validation.json` |
| Large file safeguards | Chunking policy splits large file into bounded parts | PASS | `logs/test-runs/run_t08_001/r_large_chunked.json` |
| Resilience | Retry + partial-failure continuation + segment reporting | PASS | `logs/test-runs/run_t08_001/r5_results.json`, `r5_segments.json`, `r5_summary.json` |
| Notifications | Standardized status/severity payload generated | PASS | `logs/test-runs/run_t08_001/r5_notification.json` |
| Visual fidelity review | Regression sample checklist pass/fail recorded | PASS | `logs/test-runs/run_t08_visual_001/t08.3-visual-review.json` |
| Acceptance matrix | Requirement-to-scenario mapping (R1..R7) defined | PASS | `docs/acceptance-matrix.md` |
| Workflow variants | Baseline/retry/publication/rerun JSON artifacts available | PASS | `workflow/*.json` |

## 2) Go/No-Go criteria

Release recommendation: **GO (with limitations below)**.

Conditions met:

- T08.2 scenario run succeeded (`failed=0`).
- T08.3 visual review run succeeded (`failed_samples=0`).
- Required evidence artifacts are versioned and linkable from docs.

## 3) Known limitations

1. **Synthetic fixtures in repository**
   - Current evidence uses minimal synthetic PDFs for repeatability, not production-complex documents.
2. **No live external translation provider verification in T08 runs**
   - Resilience tests validate retry/failure mechanics via deterministic command exits, not real API/network behavior.
3. **Visual checks are heuristic and metadata-driven**
   - The current T08.3 script records checklist statuses and artifact validity, but is not a pixel-diff engine.
4. **Runtime CLI availability remains environment-dependent**
   - `pdf2zh-next` binary presence and provider credentials are still deployment prerequisites.

## 4) Mitigations and follow-ups

- For limitation 1:
  - Add representative real-world corpus and re-run T08.2/T08.3 in staging before production cut.
- For limitation 2:
  - Add periodic canary run against each configured provider with sanitized sample and quota-safe limits.
- For limitation 3:
  - Introduce visual diff tooling (e.g., page image render + thresholded diff) and include artifact snapshots in reports.
- For limitation 4:
  - Add preflight checklist in deployment pipeline (`pdf2zh-next --help`, env var presence, provider connectivity).

## 5) Operational sign-off template

```yaml
release_candidate: rc_YYYYMMDD
owner: <name>
reviewers:
  - <name>
  - <name>
checklist_status: PASS
known_limitations_acknowledged: true
go_decision: GO
notes: >
  Proceed with staged rollout and canary monitoring.
```
