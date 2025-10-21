"""
Filesystem utilities
"""
import os
from pathlib import Path

def get_path(relative_path: str) -> str:
    """Get absolute path from project root"""
    root = Path(__file__).parent.parent.parent
    return str(root / relative_path)

def ensure_directories(log):
    """Ensure required directories exist"""
    data_dir = Path(get_path('data'))
    directories = ['temp', 'servers', 'plugins']
    
    for d in directories:
        dir_path = data_dir / d
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            log.info(f'{d.capitalize()} directory not found, creating it for you...')
