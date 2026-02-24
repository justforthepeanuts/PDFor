# Runtime Baseline (Phase 0 / T01.1)

Supported runtime modes:

1. **Local Python**
   - Install: `pip install pdf2zh-next`
   - Binary expected: `pdf2zh-next`

2. **Docker**
   - Image: `byaidu/pdf2zh`
   - Use n8n `Execute Command` with mounted input/output volumes.

## Baseline requirements
- Access to input and output paths.
- Translation provider credentials as needed.
- Optional `HF_ENDPOINT=https://hf-mirror.com` for restricted networks.
