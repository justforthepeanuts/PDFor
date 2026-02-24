# Artifact Naming & Versioning Convention

## Pattern
`<input>-ja_ru-<timestamp>-bilingual.pdf`

## Rules
- `<input>`: sanitized source filename without extension.
- `ja_ru`: fixed translation direction marker.
- `<timestamp>`: UTC in `YYYYMMDDTHHMMSSZ` format.
- `bilingual`: output mode marker (side-by-side).

## Example
`paper-01-ja_ru-20260224T170500Z-bilingual.pdf`
