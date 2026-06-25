#!/usr/bin/env python3
"""GCP access token üretir — n8n code node $env.GCP_ACCESS_TOKEN için."""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "execution"))

from vertex_gemini import _access_token, _load_service_account  # noqa: E402


def main() -> int:
    try:
        sa = _load_service_account()
        token = _access_token(sa)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(token)
    env_path = REPO / ".env"
    if env_path.is_file() and os.environ.get("WRITE_GCP_TOKEN_TO_ENV") == "1":
        lines = env_path.read_text().splitlines()
        out = []
        found = False
        for line in lines:
            if line.startswith("GCP_ACCESS_TOKEN="):
                out.append(f"GCP_ACCESS_TOKEN={token}")
                found = True
            else:
                out.append(line)
        if not found:
            out.append(f"GCP_ACCESS_TOKEN={token}")
        env_path.write_text("\n".join(out) + "\n")
        print("✓ .env GCP_ACCESS_TOKEN güncellendi", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
