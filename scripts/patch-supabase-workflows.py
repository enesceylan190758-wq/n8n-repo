#!/usr/bin/env python3
"""Backward-compat wrapper — use execution/patch-supabase-workflows.py"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parent.parent / "execution" / "patch-supabase-workflows.py"))
