# Implementation Plan: n8n Workflow for Japanese→Russian Scientific PDF Translation

## Goal
Deliver an automated, resilient n8n-driven pipeline that translates Japanese scientific PDFs to Russian using **PDFMathTranslate-next** as the mandatory translation/reconstruction engine, while preserving layout, formulas, tables, figures, styles, and reading structure.

## Scope & Constraints
- **Primary engine (non-negotiable):** `pdf2zh-next` / PDFMathTranslate-next only.
- **Primary direction:** `--lang-in ja --lang-out ru`.
- **Output mode:** bilingual output as default deliverable, with persistent downloadable artifact(s).
- **Automation host:** n8n workflow with robust observability and failure recovery.
- **No replacement architecture:** no custom OCR→translate→rebuild pipeline that bypasses PDFMathTranslate-next.

## Execution Phases

### Phase 0 — Foundation & Environment Baseline
**Objective:** Establish predictable runtime and dependency baseline.

1. Define runtime profile(s): local Python, Docker image (`byaidu/pdf2zh`), and optional hosted runner.
2. Standardize executable contract for n8n `Execute Command` node.
3. Verify base command compatibility (`-h`, service selection flags, language flags, output flags).
4. Define environment variables for external services and network constraints (e.g., `HF_ENDPOINT` mirror).

**Deliverables**
- Environment variable matrix.
- Canonical command template(s).
- Readiness checklist for worker host.

---

### Phase 1 — Input Intake, Validation, and Routing
**Objective:** Accept valid single-file and batch requests; reject invalid inputs safely.

1. Implement input contract in n8n (single file, multiple files, directory-style batch descriptor).
2. Add file validation gates:
   - extension/MIME checks,
   - encrypted/corrupt PDF detection,
   - file accessibility checks.
3. Add scanned-PDF heuristic routing:
   - if heavily scanned, emit warning and require OCR preprocessing path or OCR workaround policy.
4. Normalize jobs into a queue-able payload format.

**Deliverables**
- Input schema definition.
- Validation and rejection/error taxonomy.
- Standardized job payload for downstream nodes.

---

### Phase 2 — Translation Command Orchestration
**Objective:** Build deterministic command generation per job/page subset.

1. Compose command arguments from job payload:
   - `--lang-in ja --lang-out ru`
   - service selection (OpenAI/DeepL/Google/Ollama etc.)
   - `--output` location
   - optional `--pages` for partial reruns
   - `--pool-max-workers` for controlled parallelism
2. Add advanced quality controls:
   - `--custom-system-prompt` for scientific terminology,
   - `--glossaries` for fixed terms,
   - font configuration (`--primary-font-family`) for Cyrillic reliability.
3. Standardize cache behavior (`--ignore-cache` as fallback knob, not default).
4. Persist full command/audit metadata per run for reproducibility.

**Deliverables**
- Command builder spec.
- Parameter precedence rules.
- Reproducibility/audit log format.

---

### Phase 3 — Robustness, Retry, and Fallback Strategy
**Objective:** Ensure partial failure does not collapse full workflow.

1. Implement retry policy by error class:
   - transient network/service errors,
   - rate limits,
   - model endpoint unavailability.
2. Implement translation service fallback chain while preserving progress.
3. Introduce large-file safeguards:
   - chunking strategy (page partitions),
   - worker limits to avoid memory exhaustion.
4. Guarantee atomic output writes and corrupted-artifact prevention.
5. Guarantee partial completion reporting: unaffected pages/files continue when possible.

**Deliverables**
- Error classification matrix.
- Retry/fallback policy and limits.
- Partial-success output contract and notification format.

---

### Phase 4 — Layout Fidelity & Content Preservation Controls
**Objective:** Validate that reconstruction quality satisfies scientific-document constraints.

1. Define fidelity checks for:
   - formulas (kept intact),
   - tables/cell alignment,
   - list markers,
   - headers/footers/page numbers,
   - figure/text placement and multi-column structure.
2. Define overflow handling expectations for longer Russian text (dynamic scaling/panel fitting).
3. Enforce page coherence rule: same page count when feasible, structured overflow otherwise.
4. Define bilingual output naming and storage convention.

**Deliverables**
- Fidelity acceptance checklist.
- Artifact naming/versioning convention.
- Manual and automated review criteria.

---

### Phase 5 — Image/OCR Path for Embedded Japanese Text
**Objective:** Cover text in images, diagrams, and scanned regions.

1. Define OCR trigger policy and tool selection (Tesseract/EasyOCR/PaddleOCR as pre-processing support path).
2. Route extracted image text through the same translation controls (prompts/glossary/context).
3. Define reinsertion policy:
   - replace text in-image where safe,
   - otherwise add annotation overlay with position fidelity.
4. Flag low-confidence OCR segments for user review.

**Deliverables**
- OCR decision tree.
- Confidence threshold policy.
- Reinsertion/annotation guidelines.

---

### Phase 6 — n8n Workflow Design & UX Integration
**Objective:** Implement an operator-friendly automation flow with clear status visibility.

1. Build n8n node graph:
   - trigger/input nodes,
   - validation/router,
   - command execution,
   - retry/fallback branch,
   - artifact publication/notification.
2. Add structured logging and run-level trace IDs.
3. Add output access mechanism (download link/API path/output folder handoff).
4. Support optional targeted re-run by page range (`--pages`) without full reprocessing.

**Deliverables**
- n8n workflow JSON (versioned).
- Operational runbook.
- User-facing status and error messages.

---

### Phase 7 — Verification, UAT, and Operational Hardening
**Objective:** Validate against requirements and prepare for production use.

1. Create test suite matrix by scenario:
   - single PDF,
   - batch set,
   - scanned warning path,
   - large PDF memory stress,
   - rate-limit fallback,
   - partial failure continuity,
   - table/formula-heavy papers.
2. Execute visual regression sampling for layout fidelity.
3. Validate multilingual edge behavior for ja→ru typography and jargon.
4. Finalize SLO-like operational targets (success rate, time-to-complete bands, error budget).

**Deliverables**
- Acceptance test report mapped to requirements groups.
- Production readiness checklist.
- Known limitations and mitigation notes.

## Cross-Cutting Standards
- **Observability:** structured logs, command metadata, per-page/per-file status.
- **Idempotency:** safe re-runs with deterministic output paths.
- **Security:** protect API keys, sanitize paths, avoid unsafe shell interpolation.
- **Performance:** controlled concurrency and bounded memory behavior.
- **Traceability:** link every run to input hash, command args, output artifacts, and error details.

## Planned Milestones
1. **M1:** Environment + input validation complete.
2. **M2:** Command orchestration + baseline translation runs in n8n.
3. **M3:** Retry/fallback + partial completion behavior stable.
4. **M4:** Fidelity and OCR paths validated.
5. **M5:** UAT sign-off and production handoff.

## Definition of Done
The plan is considered successfully executed when:
- All requirement groups are covered by implemented workflow behavior,
- PDFMathTranslate-next is the actual execution engine in all translation paths,
- Bilingual ja→ru artifacts are reliably produced and downloadable,
- Failures are isolated, observable, and recoverable without corrupt outputs,
- Layout fidelity (formulas/tables/styles/positions) meets acceptance checks.