"""
Logger setup and utilities
"""
import logging
import sys
from pathlib import Path

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green  
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f'{log_color}{record.levelname}{self.RESET}'
        return super().format(record)

def setup_logger(name: str, debug: bool = None, log_to_file: bool = None) -> logging.Logger:
    """Setup and configure logger"""
    # Load config if available
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'config'))
        from config import DEBUG, SAVE_LOGS
        if debug is None:
            debug = DEBUG
        if log_to_file is None:
            log_to_file = SAVE_LOGS
    except:
        if debug is None:
            debug = False
        if log_to_file is None:
            log_to_file = False
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(console_handler)
    
    # File handler if enabled
    if log_to_file:
        log_dir = Path(__file__).parent.parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / f'{name}.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        logger.addHandler(file_handler)
    
    # Add convenience methods
    logger.success = lambda msg: logger.info(f'✓ {msg}')
    logger.warn = logger.warning
    
    return logger
