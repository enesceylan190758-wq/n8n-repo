#!/usr/bin/env python3
"""Backward-compat wrapper — use execution/import-workflows.py"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parent.parent / "execution" / "import-workflows.py"))
