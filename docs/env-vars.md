# Environment Variables & Secrets (T01.3)

## Required (depending on selected service)
- `OPENAI_API_KEY`
- `DEEPL_AUTH_KEY`
- `GOOGLE_API_KEY` (if Google-backed translation mode is used)
- `HF_ENDPOINT` (optional mirror endpoint for model downloads)

## Operational
- `N8N_RUN_ID` (injected by workflow for correlation)
- `PDFINATOR_OUTPUT_DIR` (default artifact directory)

## Handling policy
- Never hardcode secrets in workflow JSON.
- Inject via n8n credentials / environment.
- Redact in logs and test evidence.
