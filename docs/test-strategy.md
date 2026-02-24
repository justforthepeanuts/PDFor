# Test Strategy for PDFinator Workflow (ja→ru)

## 1) Purpose
This document defines **how testing is organized throughout execution of `tasks.md`**, not only at the end.
It complements backlog execution with explicit gates, test suites, artifacts, and pass/fail criteria.

## 2) Principles
- Test continuously per phase (shift-left), not just before release.
- Every requirement group (R1..R7) must be covered by one or more executable tests.
- Use PDFMathTranslate-next (`pdf2zh-next`) as the translation/reconstruction engine in all E2E tests.
- Prefer deterministic test datasets and reproducible command templates.
- Capture run metadata (`run_id`, `job_id`, command, service, output path, exit code).

## 3) Test Levels and Cadence

### 3.1 PR Smoke (each change)
Goal: fail fast on integration breaks.
- CLI availability and key flags.
- Input validation sanity checks.
- Command builder generation checks.
- n8n workflow JSON schema/sanity check via `ajv` or n8n's own import dry-run (if workflow JSON changed).

### 3.2 Phase Integration (at end of each task block)
Goal: prove block-level readiness before moving on.
- End of T02: intake + validation scenarios.
- End of T03: deterministic command generation and baseline translation run.
- End of T04: retries, fallback, partial failure continuation.
- End of T05/T06: fidelity + OCR branches.

### 3.3 Nightly/Regression
Goal: catch drift and service instability.
- Batch suite on representative PDFs.
- Rate-limit/fallback simulation.
- Visual fidelity spot checks.

### 3.4 Release/UAT Gate
Goal: acceptance against requirements before milestone M5 closure.
- Full R1..R7 acceptance matrix.
- Known limitations recorded and approved.

## 4) Requirement Coverage Matrix (R1..R7)

| Req Group | Coverage Focus | Primary Task Links | Test Type |
|---|---|---|---|
| R1 Upload/Input | valid PDF, batch, invalid/corrupt/password, scanned warning | T02.1–T02.5 | Integration + Negative |
| R2 Parsing/Extraction | formulas/tables/layout/lists/headers-footers | T05.1, T05.4, T08.3 | Fidelity + Visual |
| R3 Translation | ja→ru quality controls, service selection/fallback | T03.2, T03.5, T04.3 | Integration + Resilience |
| R4 Reconstruction/Output | bilingual output, layout preservation, page coherence | T05.2, T05.3, T08.3 | E2E + Visual |
| R5 Robustness | retry/backoff, OOM handling, atomic outputs, partial success | T04.1–T04.6, T07.2 | Resilience |
| R6 OCR/Image text | detect OCR need, route image text, confidence warnings | T06.1–T06.5 | Integration + Quality |
| R7 n8n/UI integration | exec-node orchestration, output handoff, partial page rerun | T07.1–T07.5, T08.2 | E2E |

## 5) Phase Gates (Definition of Ready-to-Proceed)

### Gate G1 (after T01)
- CLI contract documented and verified.
- Env/secrets map defined.
- Command template ready for n8n.

### Gate G2 (after T02)
- Invalid/corrupt/password files are rejected with clear errors.
- Scanned-page warning path is active.
- Queue payload normalization is stable.

### Gate G3 (after T03)
- Command builder deterministic for same input.
- Required args always present (`--lang-in ja --lang-out ru --output`).
- Prompt/glossary/font options validated.

### Gate G4 (after T04)
- Retry/backoff works for transient failures.
- Service fallback preserves progress.
- Partial failures do not corrupt successful outputs.

### Gate G5 (after T05+T06)
- Bilingual outputs generated and retrievable.
- Fidelity checklist pass rate is within accepted threshold.
- OCR branch supports confidence warnings and reinsertion policy.

### Gate G6 (after T07+T08)
- Full n8n E2E path stable for single + batch + partial rerun.
- Acceptance matrix R1..R7 is green or has approved exceptions.

## 6) Test Data Set (minimum)
- `sample_single_scientific.pdf` — baseline ja scientific paper.
- `sample_batch_01..N.pdf` — mixed complexity for batch mode.
- `sample_scanned.pdf` — scanned pages to trigger warning/OCR path.
- `sample_formula_heavy.pdf` — LaTeX-heavy content.
- `sample_table_multicolumn.pdf` — tables + multi-column layout.
- `sample_corrupt.pdf` — corrupted file negative case.
- `sample_password.pdf` — encrypted file negative case.

> Keep these fixtures versioned and immutable; changes require note in changelog.

## 7) Pass/Fail Criteria

### Functional
- Exit codes and node statuses align with expected outcomes.
- Invalid inputs fail early with user-readable reason.
- Successful runs produce bilingual output artifact.

### Fidelity
- Formulas preserved: 0 math tokens mistranslated in spot-check sample of ≥10 pages per run.
- Table structure/cell alignment preserved: ≥95% of cells in sample retain correct row/column mapping.
- Visual regression: no layout shift >5px on reference page comparisons (tool: diff-pdf or manual review log).

### Resilience
- Retries are bounded and logged.
- Fallback service path produces continued progress when available.
- No corrupted partial PDF written on interruption.

## 8) Evidence and Reporting
For each executed suite, store:
- run metadata (`run_id`, commit, environment, service)
- command and parameters (sanitized)
- output artifact path(s)
- concise verdict (PASS/FAIL/WARN) and failure reason

Storage target (choose one per deployment):
- Local worker FS: `logs/test-runs/<date>/<suite>.md`
  + `logs/test-runs/<date>/artifacts/`
- n8n execution logs: attach evidence as workflow execution annotation or Binary node output.
- Object storage (S3/MinIO): bucket `pdf-inator-logs/<date>/ <run_id>/` — preferred for Docker/remote deployments.

## 9) Ownership Model
- Developer implements and runs PR smoke + relevant integration tests.
- Reviewer verifies evidence completeness and gate criteria.
- Release owner approves UAT matrix and known limitations.

## 10) Mapping to `tasks.md`
- Use this document as execution policy for all `Type: Test` tasks (T01.2, T05.3, T05.4, T08.*).
- For each completed task, attach evidence links to the corresponding backlog item.