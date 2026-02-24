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

## Task execution kickoff

Initial execution has started with foundational setup and documentation tasks to unblock implementation work.
