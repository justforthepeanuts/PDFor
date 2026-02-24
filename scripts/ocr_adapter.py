#!/usr/bin/env python3
"""Tool-agnostic OCR preprocessing adapter (T06.2)."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List


def _load(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def _build_command(provider_cfg: Dict[str, Any], input_path: Path, output_dir: Path) -> List[str]:
    output_base = output_dir / input_path.stem
    output_json = output_dir / f"{input_path.stem}.json"
    cmd = [provider_cfg["binary"]]
    for token in provider_cfg.get("args", []):
        cmd.append(
            token.format(
                input=str(input_path),
                output_base=str(output_base),
                output_json=str(output_json),
            )
        )
    return cmd


def run_adapter(
    input_path: Path,
    provider: str,
    config: Dict[str, Any],
    output_dir: Path,
    dry_run: bool,
) -> Dict[str, Any]:
    providers = config.get("providers", {})
    if provider not in providers:
        return {"status": "FAIL", "reason": f"unsupported_provider:{provider}"}

    provider_cfg = providers[provider]
    cmd = _build_command(provider_cfg, input_path, output_dir)

    result: Dict[str, Any] = {
        "status": "PASS",
        "provider": provider,
        "input": str(input_path),
        "command": cmd,
        "output_dir": str(output_dir),
        "ocr_required": True,
    }

    if dry_run:
        result["dry_run"] = True
        return result

    binary = provider_cfg.get("binary")
    if not shutil.which(binary):
        return {
            "status": "FAIL",
            "provider": provider,
            "input": str(input_path),
            "command": cmd,
            "reason": f"missing_binary:{binary}",
        }

    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return {
            "status": "FAIL",
            "provider": provider,
            "input": str(input_path),
            "command": cmd,
            "reason": "ocr_command_failed",
            "stderr": proc.stderr[-500:],
            "returncode": proc.returncode,
        }

    result["returncode"] = proc.returncode
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run OCR provider adapter")
    parser.add_argument("input", type=Path, help="Image/PDF path for OCR preprocessing")
    parser.add_argument("--provider", type=str, help="OCR provider key")
    parser.add_argument("--config", type=Path, default=Path("configs/ocr-tools.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("logs/ocr"))
    parser.add_argument("--result-out", type=Path, default=Path("logs/ocr/result.json"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cfg = _load(args.config)
    provider = args.provider or cfg.get("default_provider", "tesseract")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    result = run_adapter(args.input, provider, cfg, args.output_dir, args.dry_run)

    args.result_out.parent.mkdir(parents=True, exist_ok=True)
    args.result_out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result.get("status"), "provider": provider, "result": str(args.result_out)}))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
