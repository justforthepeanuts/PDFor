# Persistent Context for PDF Translation Workflow Project (Updated Feb 21, 2026)

**Core Tool (Design Constraint)**: PDFMathTranslate-next (GitHub: https://github.com/PDFMathTranslate/PDFMathTranslate-next) — Use ALWAYS as main engine; NO alternatives (e.g., no custom pdf→text→translate→pdf). Backend: BabelDOC (https://github.com/funstory-ai/BabelDOC).

**Supported Languages**: Multi-language (e.g., en→zh, ja→en/zh/tr/ru, multi via --lang-in --lang-out). Japanese (ja) to Russian (ru) supported via --lang-in ja --lang-out ru.

**Installation/Setup**:
- pip install pdf2zh-next; 
- Docker pull byaidu/pdf2zh; 
- WebUI/GUI via gradio app; 
- Windows ZIP releases (e.g., pdf2zh-v2.8.2-BabelDOC-with-assets-win64.zip);
- Zotero plugin (guaguastandup/zotero-pdf2zh) for direct translate.

**CLI Flags/Params (from USAGE_commandline.html and ADVANCED.md)**:
- Input: input-files (local files or multiple for batch e.g., pdf2zh file1.pdf file2.pdf).
- Languages: --lang-in [source] --lang-out [target] (e.g., --lang-in ja --lang-out ru).
- Service: Selection via individual CLI flags, e.g., --openai, --deepseek, --deepl, --google, etc.; list of available services via pdf2zh_next -h.
- Partial: --pages "1,3,5-7" (comma-separated, ranges).
- Multi-thread: --pool-max-workers [num] (workers for parallel).
- Output: --output /path/ [dir] (saves translated PDFs); bilingual dual.pdf (side-by-side) vs monolingual mono.pdf (default both).
- Filters: --custom-system-prompt [file] (prompt for jargon); --glossaries "glossary.csv" (term glossary); --primary-font-family [font] (font override); --ignore-cache (ignore cache); no -f/-c regex, --skip-subset-fonts, --compatible, --onnx, --mcp --sse (not documented).

**Key Features (from README/ADVANCED.md/arXiv)**:
- Layout Parsing: DocLayout-YOLO (ONNX) for detecting blocks/formulas (LaTeX)/tables/figures/multi-column/TOC/annotations/cross-page; chunking with metadata (bbox, font/size/baseline/positioning/style).
- Text Extraction: Auto with Pdfminer.six/PyMuPDF; MinerU for advanced (in 2.7+); handles rare cases (insets) via layout.
- Translation: Middleware for chunks via services (Google/DeepL/Ollama/OpenAI); contextual (scientific jargon, partial for tables/formulas); leave LaTeX/formulas intact; translate descriptions.
- Reconstruction: Re-rendering with translated text in bbox; dynamic scaling/resizing fonts/panels for length differences; preserved graphics/styles without distortions; bilingual (side-by-side).
- Batch: Loop over files/dir (multiple inputs); for academic papers/reviewers (Zotero batch).
- Plugins: Zotero for direct translate; Gradio PDF for preview.

**Gotchas/Limitations/Error Handling (from README/issues/X posts)**:
- Scanned PDFs: Need pre-OCR (no built-in); fallback issues in word-conversion (merged paragraphs); use --ocr-workaround (black-on-white force), --auto-enable-ocr-workaround (auto for heavy scanned).
- Large PDFs: Memory issues — chunk pages (--max-pages-per-part 50); use --pool-max-workers for parallel; skips large pages.
- Japanese Kanji/Russian Cyrillic: Supported, but font mapping/resize required (--primary-font-family); issues with idioms/accuracy — use --custom-system-prompt or --glossaries.
- Errors: No explicit retries; propagate exceptions; use --ignore-cache; network — HF_ENDPOINT=https://hf-mirror.com for models (restricted networks); --debug for logs; rate limits on DeepL/Google (use Ollama fallback).
- Updates 2025-2026: BabelDOC backend integrated (no --babeldoc, always on); v2.0 release May 2025 (not dev-only; current v2.8.2 Dec 2025, improved consistency with font/term fixes, table text translation exp, cache cleanup Aug 2025).

All requirements MUST tie to these features; cover normal/edge (e.g., scanned/large/ja-kanji), error handling, persistence (output PDFs), UI (GUI/n8n integration).