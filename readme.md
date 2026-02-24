# PDFor Project Structure

This repository contains planning and execution artifacts for an n8n-driven PDF translation workflow based on PDFMathTranslate-next.

## Repository layout

- `requirements.md` — product requirements and acceptance criteria (R1..R7).
- `context.md` — technical constraints and tool-specific context.
- `plan.md` — phased implementation plan.
- `tasks.md` — execution backlog with dependencies.
- `test-strategy.md` — test cadence, gates, and coverage.
- `document-analysis.md` — cross-document analysis summary.

### Execution directories (started from `tasks.md`)

- `workflow/` — versioned n8n workflow JSON artifacts.
- `scripts/` — helper scripts for validation/orchestration.
- `configs/` — runtime/provider configuration assets.
- `docs/` — supporting operational documentation.
- `logs/` — run/test evidence and execution logs.

### Docs added while starting task execution

- `docs/artifact-naming.md` (T00.2)
- `docs/run-id-standard.md` (T00.3)
- `docs/runtime-baseline.md` (T01.1)
- `docs/env-vars.md` (T01.3)
- `docs/command-template.md` (T01.4)
- `docs/intake-validation.md` (T02.1..T02.5)
- `configs/input-schema.json`, `scripts/validate_input.py`, and `scripts/normalize_jobs.py` for intake checks and queue payload normalization
- `configs/services.json`, `scripts/build_commands.py`, and `docs/command-orchestration.md` for deterministic command generation and audit logging
- `docs/resilience-policy.md`, `scripts/execute_with_resilience.py`, and `scripts/plan_page_chunks.py` for retry/backoff, fallback execution, large-file chunking, atomic result writes, and partial-failure reporting
- `docs/fidelity-checklist.md` and `scripts/verify_bilingual_artifacts.py` for measurable fidelity checks and bilingual output verification hooks
- `docs/fidelity-regression.md`, `scripts/check_page_coherence.py`, `scripts/validate_regression_manifest.py`, and `configs/regression-samples.json` for T05.3/T05.4 overflow checks and regression sample validation
- `docs/ocr-decision-tree.md`, `configs/ocr-tools.json`, and `scripts/ocr_adapter.py` for T06.1/T06.2 OCR routing and adapter integration
- `docs/ocr-translation-routing.md` and `scripts/route_ocr_segments.py` for T06.3/T06.5 OCR-to-translation routing and low-confidence warning outputs
- `docs/ocr-reinsertion-policy.md` and `scripts/plan_reinsertion.py` for T06.4 replace-vs-annotation reinsertion planning
- `workflow/baseline-workflow.json` and `docs/workflow-baseline.md` for T07.1 baseline n8n flow assembly
- `workflow/retry-fallback-workflow.json`, `docs/workflow-retry-notify.md`, and `scripts/format_error_notification.py` for T07.2 retry/fallback branching and standardized notifications
- `workflow/publication-workflow.json`, `scripts/publish_outputs.py`, and `docs/workflow-output-publication.md` for T07.3 output publication (direct link/API/folder handoff)
- `scripts/emit_trace_log.py` and `docs/workflow-trace-logging.md` for T07.4 structured trace logging at workflow branch boundaries
- `workflow/page-rerun-workflow.json`, `scripts/apply_rerun_pages.py`, and `docs/workflow-page-rerun.md` for T07.5 targeted page-range reruns (`--pages`)
- `docs/acceptance-matrix.md` for T08.1 requirement-to-scenario acceptance mapping (R1..R7)
- `scripts/run_t08_scenarios.py`, `docs/t08-scenario-results.md`, and `logs/test-runs/run_t08_001/` for T08.2 executed scenario evidence
- `samples/*.pdf`, `scripts/run_t08_visual_review.py`, `docs/t08-visual-review-results.md`, and `logs/test-runs/run_t08_visual_001/` for T08.3 visual-fidelity review evidence
- `docs/production-readiness.md` for T08.4 release checklist, known limitations, and mitigations

## Task execution kickoff

Initial execution has started with foundational setup and documentation tasks to unblock implementation work.
