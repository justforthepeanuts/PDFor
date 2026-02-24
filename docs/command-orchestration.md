# Command Orchestration (T03.1..T03.6)

## Artifacts
- Service strategy config: `configs/services.json`
- Command builder: `scripts/build_commands.py`

## Coverage
- T03.1 deterministic base command with required args.
- T03.2 service selection through config-driven flag mapping.
- T03.3 optional page-range rerun support (`--pages`).
- T03.4 controlled concurrency (`--pool-max-workers`, min 1 clamp).
- T03.5 quality controls (`--custom-system-prompt`, `--glossaries`, `--primary-font-family`).
- T03.6 command/audit persistence (`--output` JSON and `--audit-out` JSONL).

## Usage
```bash
python scripts/build_commands.py normalized-jobs.json \
  --service-config configs/services.json \
  --output logs/commands.json \
  --audit-out logs/commands.audit.jsonl
```

## Determinism notes
- Arguments are emitted in fixed order.
- Optional flags are appended in a stable sequence.
- `command_hash` is stored per record for reproducibility checks.
