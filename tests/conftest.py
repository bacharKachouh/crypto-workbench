"""Pytest configuration — puts the plugin's src/ on the path so modules
are importable the same way the skills invoke them (PYTHONPATH=src).
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
