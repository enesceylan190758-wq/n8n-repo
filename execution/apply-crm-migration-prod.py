#!/usr/bin/env python3
"""Prod Supabase'e CRM Phase 1 migration uygular.

Kullanım:
  SUPABASE_DB_URL='postgresql://postgres.[ref]:[PASSWORD]@...' python3 execution/apply-crm-migration-prod.py
  # veya Supabase Dashboard → SQL Editor → supabase/migrations/20260727120000_crm_stella_phase1.sql
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "supabase" / "migrations" / "20260727120000_crm_stella_phase1.sql"


def main() -> None:
    db_url = os.environ.get("SUPABASE_DB_URL") or os.environ.get("DATABASE_URL")
    if not db_url:
        print("SUPABASE_DB_URL yok — migration'ı Supabase SQL Editor'da çalıştırın:")
        print(f"  {MIGRATION}")
        sys.exit(0)
    if not MIGRATION.exists():
        raise SystemExit(f"Migration bulunamadı: {MIGRATION}")
    cmd = [
        "npx", "--yes", "supabase@latest", "db", "push",
        "--db-url", db_url,
        "--yes",
    ]
    print("Running:", " ".join(cmd[:6]), "...")
    subprocess.run(cmd, cwd=ROOT, check=True)
    print("Migration applied.")


if __name__ == "__main__":
    main()
