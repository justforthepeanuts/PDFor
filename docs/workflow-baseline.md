# Baseline n8n Workflow (T07.1)

Implemented file:
- `workflow/baseline-workflow.json`

## Path covered
`trigger -> validate -> normalize -> build command -> execute -> collect artifacts`

## Nodes
1. **Manual Trigger**
2. **Validate Input** (`scripts/validate_input.py`)
3. **Normalize Jobs** (`scripts/normalize_jobs.py`)
4. **Build Commands** (`scripts/build_commands.py`)
5. **Execute With Resilience** (`scripts/execute_with_resilience.py`)
6. **Collect Artifacts** (Code node exporting key output paths)

## Produced outputs
- jobs JSON
- commands JSON
- command audit JSONL
- execution results JSON
- problem segments JSON
- execution summary JSON

## Notes
- This is the baseline T07.1 graph; retry/fallback branching enhancements are tracked separately in T07.2.
