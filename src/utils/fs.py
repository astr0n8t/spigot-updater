"""
Filesystem utilities
"""
import os
from pathlib import Path

def path(relative_path: str) -> str:
    """Get absolute path from project root"""
    root = Path(__file__).parent.parent.parent
    return str(root / relative_path)

def ensure_directories(log):
    """Ensure required directories exist"""
    root = Path(__file__).parent.parent.parent
    directories = [
        root / 'data',
        root / 'data' / 'servers',
        root / 'data' / 'plugins',
        root / 'logs',
        root / 'config'
    ]
    
    for directory in directories:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            log.info(f'Created directory: {directory}')
