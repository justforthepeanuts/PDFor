# n8n Execute Command Template (T01.4)

## Base template
```bash
pdf2zh-next "{{ $json.input_file }}" \
  --lang-in ja \
  --lang-out ru \
  --output "{{ $json.output_dir }}"
```

## Optional parameters
- Service selector: `--openai` / `--deepl` / `--google`
- Partial rerun: `--pages "{{ $json.page_range }}"`
- Parallel workers: `--pool-max-workers {{ $json.pool_max_workers || 2 }}`
- Glossary: `--glossaries "{{ $json.glossary_path }}"`
- Prompt: `--custom-system-prompt "{{ $json.prompt_path }}"`
- Font stabilization: `--primary-font-family "{{ $json.primary_font || 'Noto Sans' }}"`
