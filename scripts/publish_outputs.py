#!/usr/bin/env python3
"""Create publication payloads for workflow outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _build_direct_link(base_url: str, path_value: str) -> str:
    return f"{base_url.rstrip('/')}/{path_value.lstrip('/')}"


def _collect_exports(paths: Dict[str, Any], base_url: str) -> List[Dict[str, str]]:
    exports: List[Dict[str, str]] = []
    for key, value in paths.items():
        if not isinstance(value, str) or not value:
            continue
        exports.append(
            {
                "artifact": key,
                "path": value,
                "link": _build_direct_link(base_url, value),
            }
        )
    return exports


def main() -> int:
    parser = argparse.ArgumentParser(description="Build output publication payload")
    parser.add_argument("--artifacts", required=True, help="Path to collected artifacts JSON")
    parser.add_argument("--run-id", required=True, help="Run identifier")
    parser.add_argument("--publication-mode", choices=["link", "api", "folder"], default="link")
    parser.add_argument("--public-base-url", default="https://files.local")
    parser.add_argument("--api-endpoint", default="https://api.local/v1/pdfor/runs")
    parser.add_argument("--handoff-dir", default="handoff")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    artifacts = _read_json(Path(args.artifacts))
    exports = _collect_exports(artifacts, args.public_base_url)

    publication: Dict[str, Any] = {
        "run_id": args.run_id,
        "mode": args.publication_mode,
        "artifacts": exports,
    }

    if args.publication_mode == "link":
        publication["delivery"] = {
            "type": "direct_link",
            "primary": exports[0]["link"] if exports else None,
        }
    elif args.publication_mode == "api":
        publication["delivery"] = {
            "type": "api_response",
            "endpoint": f"{args.api_endpoint.rstrip('/')}/{args.run_id}",
            "method": "POST",
            "payload": {"run_id": args.run_id, "artifacts": exports},
        }
    else:
        publication["delivery"] = {
            "type": "folder_handoff",
            "directory": f"{args.handoff_dir.rstrip('/')}/{args.run_id}",
            "files": [item["path"] for item in exports],
        }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(publication, ensure_ascii=False, indent=2), encoding="utf-8")
    print("PUBLICATION_READY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
