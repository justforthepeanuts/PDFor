# Requirements Document

## Introduction
The application is an automated workflow in n8n for translating scientific PDF documents from Japanese to Russian, with an emphasis on preserving the original layout, mathematical formulas (including LaTeX), tables, graphics, table of contents, annotations, styles, and element positioning. The primary tool — PDFMathTranslate — serves as a key constraint to ensure translation quality. Key functions include bilingual output, batch processing, error handling, and integration with n8n for automation.

## Requirements

### Group 1: Upload and Input Data
As a user, I want to upload or specify a PDF file or directory for translation so that I can process Japanese scientific documents efficiently.
#### Acceptance Criteria:
- WHEN the user provides a single PDF file THEN the system accepts the file and initiates processing via PDFMathTranslate.
- WHEN the user specifies a directory containing multiple PDFs (batch mode) THEN the system processes all files in parallel using -t for multi-threading, without data loss.
- WHEN a file contains scanned pages THEN the system issues a warning about the need for pre-OCR and does not proceed without it.
- WHEN the uploaded PDF is password-protected or corrupted THEN the system SHALL notify the user that the file cannot be processed.
- WHEN the uploaded file is not a valid PDF THEN the system SHALL display a clear validation error message.


### Group 2: Parsing and Content Extraction
As a user, I want the system to parse the PDF layout accurately so that all elements like formulas, tables, and images are identified and preserved.
#### Acceptance Criteria:
- WHEN the PDF contains mathematical formulas (LaTeX) THEN the system detects them using DocLayout-YOLO and preserves them in their original format without translation.
- WHEN the PDF has a complex layout (multi-column, TOC, annotations, cross-page elements) THEN the system extracts text with metadata (bbox, font, size, baseline) without distortions incl. row/column alignment, nested formatting in cells.
- WHEN the file is large or contains rare cases (insets) THEN the system uses PyMuPDF/Pdfminer.six for extraction without memory errors.
- WHEN lists (bulleted or numbered) are present THEN the system recognizes structure and preserves the markers (bullets, numbers) for restoration.
- WHEN the document contains headers, footers, and page numbers, THEN the system extracts them as separate elements linked to their position.
- WHEN text positioning is complex THEN the system SHALL maintain relative placement consistency.

### Group 3: Text Translation
As a user, I want the text to be translated from Japanese to Russian while keeping non-text elements intact so that the document remains usable for research.
#### Acceptance Criteria:
- WHEN translating text chunks THEN the system uses middleware (DeepL/Google/Ollama/OpenAI etc) with context for scientific jargon, partial for tables/formulas, do_translate method, advanced prompting (few-shot, CoT, role-playing) via --prompt file; supports 194 languages.
- WHEN kanji or cyrillic issues occur THEN the system applies font mapping and custom --prompt to improve accuracy.
- WHEN the selected service returns an error (rate limit) THEN the system switches to an alternative (e.g., from DeepL to Ollama), preserving progress.
- WHEN non-Japanese text (e.g., numbers, Latin terms, codes) is present THEN the system SHALL preserve it unless translation is required.
- WHEN the system cannot confidently translate a fragment (e.g., rare characters, damaged text) THEN it SHALL flag or log the issue for review.

### Group 4: Reconstruction and Output
As a user, I want a bilingual PDF output with preserved styles and positions so that I can compare the original and translation side-by-side.
#### Acceptance Criteria:
- WHEN the translated text is longer than the original THEN the system applies dynamic scaling/resizing fonts/panels to fit without cropping or shifting.
- WHEN generating the output THEN it is a bilingual PDF (side-by-side) using -o for the directory and --bilingual for the format.
- WHEN reconstruction is complete THEN all graphics/styles/positions remain without distortions, testable by visual comparison.
- WHEN the document contained lists, headers, footers, page numbers, and tables, THEN they are restored in exact accordance with the original (list markers are preserved, tables are not broken).
- WHEN the document contains tables THEN the system SHALL preserve table layout and cell alignment.
- WHEN the document includes headers, footers, or page numbers THEN the system SHALL preserve their placement and formatting.
-WHEN the images contained translated text (from Group 3), THEN the system embeds the translated text back into the image, preserving the original positioning (font, size, and color are matched as closely as possible).
- WHEN the reconstruction is complete, the final PDF must have the same number of pages as the original document; if this is not possible due to differences in text volume, the system ensures logical coherence of the content (e.g., by flowing text to the next page while preserving the structure).
- WHEN the file is ready, THEN the user is given the option to download it (via a web interface, API, or a direct link to the file in the output directory).

### Group 5: Error Handling and Robustness
As a user, I want robust error handling for common issues so that the workflow does not fail unexpectedly.
#### Acceptance Criteria:
- WHEN a memory issue occurs on large PDFs THEN the system chunks pages and uses --ignore-cache to continue.
- WHEN a network error occurs for the API THEN the system propagates exceptions with logging and retries using the HF_ENDPOINT mirror.
- WHEN the translation process is interrupted (e.g., due to a power failure or user stoppage), THEN the system ensures that no corrupted partial PDF is generated (e.g., through atomic writing of temporary files).
- WHEN partial processing occurs (e.g., an error on one page), THEN the system completes the processing of the remaining pages and notifies the user about the problematic areas, without mixing corrupted data with the correct ones.

### Group 6: Processing of Images and Embedded Elements
As a user, I want text inside images, diagrams, and scanned pages to be translated, so that all visible Japanese text in the document becomes understandable.
#### Acceptance Criteria:
- WHEN the document contains images with Japanese text (charts, photos with captions, scanned pages), THEN the system detects text areas using OCR (Tesseract / EasyOCR / PaddleOCR).
- WHEN the text is extracted from the image, it is sent to the common translation pipeline (Group 3).
- WHEN the translated text is received, the system determines the optimal placement for it (replacing the original text or adding it as a pop-up annotation) while preserving the visual integrity of the image.
- WHEN the image contains no text, it is left unchanged.
- WHEN OCR quality is low (e.g., due to poor resolution), the system notifies the user about potential distortions.

### Group 7: Integration with n8n and UI/UX
As a user, I want seamless integration with n8n nodes so that the workflow is automated and easy to use.
#### Acceptance Criteria:
- WHEN the workflow is launched THEN it calls PDFMathTranslate via an exec node with CLI flags (e.g., -li ja -lo ru -s ollama).
- WHEN using a GUI or Zotero plugin THEN the system supports input from them for persistent output PDFs.
- WHEN an edge case occurs (e.g., partial pages) THEN the system uses -p for targeted translation, testable by output.