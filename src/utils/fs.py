"""
Filesystem utilities
"""
import os
from pathlib import Path

def path(relative_path: str) -> str:
    """Get absolute path from project root"""
    root = Path(__file__).parent.parent.parent
    return str(root / relative_path)
