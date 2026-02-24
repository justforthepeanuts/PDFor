# tasks.md — Execution Backlog for PDFinator

This task list operationalizes `plan.md` into implementable work items for the n8n + PDFMathTranslate-next delivery.

## Conventions
- **Test policy**: execute tests by phase gates using `docs/test-strategy.md`.
- **Priority**: P0 (critical), P1 (high), P2 (medium)
- **Status**: TODO / IN_PROGRESS / BLOCKED / DONE
- **Type**: Build / Test / Ops / Docs
- **Traceability**: each task maps to one or more requirement groups (R1..R7 from `requirements.md`)

---

## T00 — Project Setup & Governance

- [x] **T00.1** Create repository structure for workflow artifacts (`/workflow`, `/scripts`, `/configs`, `/docs`, `/logs`).  
  - Priority: P0 | Type: Build | Status: DONE  
  - Depends on: none  
  - Maps to: R7

- [x] **T00.2** Define artifact naming/versioning convention (`<input>-ja_ru-<timestamp>-bilingual.pdf`).  
  - Priority: P1 | Type: Docs | Status: DONE  
  - Depends on: T00.1  
  - Maps to: R4, R7

- [x] **T00.3** Add run ID correlation standard (`run_id`, `job_id`, `file_id`, `page_range`) across nodes/logs.  
  - Priority: P1 | Type: Ops | Status: DONE  
  - Depends on: T00.1  
  - Maps to: R5, R7

---

## T01 — Runtime Baseline (Phase 0)

- [x] **T01.1** Pin runtime options and document supported modes: local Python + Docker (`byaidu/pdf2zh`).  
  - Priority: P0 | Type: Ops | Status: DONE  
  - Depends on: T00.1  
  - Maps to: R7

- [ ] **T01.2** Validate CLI availability and flags (`pdf2zh-next -h` / language/service/output/page options).  
  - Priority: P0 | Type: Test | Status: BLOCKED  
  - Depends on: T01.1  
  - Maps to: R3, R4, R7

- [x] **T01.3** Define required secrets/env vars (`OPENAI_API_KEY`, `DEEPL_AUTH_KEY`, `HF_ENDPOINT`, etc.).  
  - Priority: P0 | Type: Ops | Status: DONE  
  - Depends on: T01.1  
  - Maps to: R3, R5, R7

- [x] **T01.4** Create command template document for n8n Execute Command node.  
  - Priority: P1 | Type: Docs | Status: DONE  
  - Depends on: T01.2, T01.3  
  - Maps to: R7

---

## T02 — Intake & Validation (Phase 1)

- [x] **T02.1** Define input schema for single file, multi-file batch, and directory payload modes.  
  - Priority: P0 | Type: Build | Status: DONE  
  - Depends on: T01.4  
  - Maps to: R1, R7

- [x] **T02.2** Implement PDF validation (MIME/ext check + readable file guard).  
  - Priority: P0 | Type: Build | Status: DONE  
  - Depends on: T02.1  
  - Maps to: R1

- [x] **T02.3** Implement corrupted/password-protected detection and explicit error messages.  
  - Priority: P0 | Type: Build | Status: DONE  
  - Depends on: T02.2  
  - Maps to: R1, R5

- [x] **T02.4** Add scanned-page heuristic; warn and route to OCR-preprocess policy.  
  - Priority: P0 | Type: Build | Status: DONE  
  - Depends on: T02.2  
  - Maps to: R1, R6

- [x] **T02.5** Normalize accepted inputs into queue-ready job payloads.  
  - Priority: P1 | Type: Build | Status: DONE  
  - Depends on: T02.1, T02.2  
  - Maps to: R1, R7

---

## T03 — Command Orchestration (Phase 2)

- [x] **T03.1** Implement deterministic command builder for required args:  
  `--lang-in ja --lang-out ru --output <dir>`.  
  - Priority: P0 | Type: Build | Status: DONE  
  - Depends on: T02.5  
  - Maps to: R3, R4, R7

- [x] **T03.2** Add service-selection strategy and config (`--openai`, `--deepl`, `--google`, etc.).  
  - Priority: P0 | Type: Build | Status: DONE  
  - Depends on: T03.1, T01.3  
  - Maps to: R3, R5

- [x] **T03.3** Add optional partial rerun support (`--pages`).  
  - Priority: P1 | Type: Build | Status: DONE  
  - Depends on: T03.1  
  - Maps to: R7

- [x] **T03.4** Add concurrency controls (`--pool-max-workers`) with safe defaults.  
  - Priority: P1 | Type: Build | Status: DONE  
  - Depends on: T03.1  
  - Maps to: R1, R5

- [x] **T03.5** Add quality controls via prompt/glossary/font config.  
  - Priority: P0 | Type: Build | Status: DONE  
  - Depends on: T03.1  
  - Maps to: R3, R4

- [x] **T03.6** Persist full command/audit metadata per run.  
  - Priority: P1 | Type: Ops | Status: DONE  
  - Depends on: T03.1  
  - Maps to: R5, R7

---

## T04 — Resilience & Fallback (Phase 3)

- [x] **T04.1** Build error taxonomy (validation, API rate limit, transient network, OOM, file-level failure).  
  - Priority: P0 | Type: Docs | Status: DONE  
  - Depends on: T03.6  
  - Maps to: R5

- [x] **T04.2** Implement retry policy with backoff for transient/API failures.  
  - Priority: P0 | Type: Build | Status: DONE  
  - Depends on: T04.1  
  - Maps to: R5

- [x] **T04.3** Implement translation service fallback chain preserving progress.  
  - Priority: P0 | Type: Build | Status: DONE  
  - Depends on: T04.2  
  - Maps to: R3, R5

- [x] **T04.4** Implement large-file safeguards (page chunking + worker caps).  
  - Priority: P0 | Type: Build | Status: DONE  
  - Depends on: T04.1  
  - Maps to: R2, R5

- [x] **T04.5** Ensure atomic outputs and no corrupted partial PDFs on interruption.  
  - Priority: P0 | Type: Build | Status: DONE  
  - Depends on: T04.1  
  - Maps to: R5

- [x] **T04.6** Continue unaffected files/pages on partial failures and report problem segments.  
  - Priority: P0 | Type: Build | Status: DONE  
  - Depends on: T04.3, T04.5  
  - Maps to: R5

---

## T05 — Fidelity Controls (Phase 4)

- [x] **T05.1** Define measurable fidelity checklist (formulas, tables, lists, TOC, headers/footers/page numbers).  
  - Priority: P0 | Type: Docs | Status: DONE  
  - Depends on: T03.1  
  - Maps to: R2, R4

- [x] **T05.2** Implement bilingual artifact policy and output verification hooks.  
  - Priority: P0 | Type: Build | Status: DONE  
  - Depends on: T03.1  
  - Maps to: R4

- [x] **T05.3** Add overflow/page-coherence checks for longer Russian content.  
  - Priority: P1 | Type: Test | Status: DONE  
  - Depends on: T05.1, T05.2  
  - Maps to: R4

- [x] **T05.4** Add regression samples for table-heavy/formula-heavy/multi-column PDFs.  
  - Priority: P1 | Type: Test | Status: DONE  
  - Depends on: T05.1  
  - Maps to: R2, R4

---

## T06 — OCR & Embedded Image Text (Phase 5)

- [x] **T06.1** Define OCR decision tree for scanned pages and image-text regions.  
  - Priority: P0 | Type: Docs | Status: DONE  
  - Depends on: T02.4  
  - Maps to: R6

- [x] **T06.2** Implement OCR preprocessing integration path (tool-agnostic adapter).  
  - Priority: P1 | Type: Build | Status: DONE  
  - Depends on: T06.1  
  - Maps to: R6

- [x] **T06.3** Route OCR text through same translation controls (prompt/glossary/service fallback).  
  - Priority: P1 | Type: Build | Status: DONE  
  - Depends on: T06.2, T03.5, T04.3  
  - Maps to: R3, R6

- [x] **T06.4** Implement reinsertion policy (replace vs annotation) with position fidelity.  
  - Priority: P1 | Type: Build | Status: DONE  
  - Depends on: T06.3  
  - Maps to: R4, R6

- [x] **T06.5** Add low-confidence OCR warnings to user-facing output.  
  - Priority: P1 | Type: Build | Status: DONE  
  - Depends on: T06.2  
  - Maps to: R6, R7

---

## T07 — n8n Workflow Assembly (Phase 6)

- [x] **T07.1** Build baseline n8n workflow JSON: trigger → validate → build command → execute → collect artifacts.  
  - Priority: P0 | Type: Build | Status: DONE  
  - Depends on: T02.5, T03.1  
  - Maps to: R7

- [x] **T07.2** Add retry/fallback branches and standardized error notifications.  
  - Priority: P0 | Type: Build | Status: DONE  
  - Depends on: T04.2, T04.3, T07.1  
  - Maps to: R5, R7

- [x] **T07.3** Add output publication node(s): direct file link/API response/folder handoff.  
  - Priority: P0 | Type: Build | Status: DONE  
  - Depends on: T07.1  
  - Maps to: R4, R7

- [x] **T07.4** Add structured logs and trace IDs at each branch boundary.  
  - Priority: P1 | Type: Ops | Status: DONE  
  - Depends on: T00.3, T07.1  
  - Maps to: R5, R7

- [x] **T07.5** Add targeted page-range rerun path in workflow (`--pages`).  
  - Priority: P1 | Type: Build | Status: DONE  
  - Depends on: T03.3, T07.1  
  - Maps to: R7

---

## T08 — Verification & Readiness (Phase 7)

- [x] **T08.1** Create acceptance test matrix mapped to R1..R7.  
  - Priority: P0 | Type: Test | Status: DONE  
  - Depends on: T07.1, T07.2, T07.3  
  - Maps to: R1, R2, R3, R4, R5, R6, R7

- [ ] **T08.2** Execute scenario tests: single file, batch, scanned warning, large file, rate limit, partial failure continuity.  
  - Priority: P0 | Type: Test | Status: TODO  
  - Depends on: T08.1  
  - Maps to: R1, R5, R7

- [ ] **T08.3** Run visual fidelity review samples and record pass/fail per checklist item.  
  - Priority: P1 | Type: Test | Status: TODO  
  - Depends on: T05.1, T08.1  
  - Maps to: R2, R4

- [ ] **T08.4** Publish production readiness checklist + known limitations + mitigations.  
  - Priority: P1 | Type: Docs | Status: TODO  
  - Depends on: T08.2, T08.3  
  - Maps to: R5, R7

---

## Milestone Mapping
- **M1** (Foundation): T00 + T01 + T02
- **M2** (Baseline translation flow): T03 + T07.1 + T07.3
- **M3** (Resilience): T04 + T07.2 + T07.4
- **M4** (Fidelity + OCR): T05 + T06
- **M5** (Readiness): T08

## Immediate Next Actions (Sprint 1)
1. Complete T01.1–T01.4 (runtime and command contract).
2. Complete T02.1–T02.5 (intake and validation pipeline).
3. Complete T03.1 + T07.1 for first end-to-end happy path.
4. Add T04.2/T04.3 retry-fallback to stabilize early runs.