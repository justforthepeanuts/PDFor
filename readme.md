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

## Task execution kickoff

Initial execution has started with foundational setup and documentation tasks to unblock implementation work.
