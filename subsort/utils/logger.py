"""
Logging utility for SubSort
Provides structured logging with different levels and output options
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

def setup_logger(verbose: bool = False, log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup logger with appropriate configuration
    
    Args:
        verbose: Enable debug level logging
        log_file: Optional custom log file path
        
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger('subsort')
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler (only for warnings and errors unless verbose)
    console_handler = logging.StreamHandler(sys.stderr)
    if verbose:
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        file_path = Path(log_file)
    else:
        # Create logs directory if it doesn't exist
        logs_dir = Path('logs')
        logs_dir.mkdir(exist_ok=True)
        
        # Generate timestamped log file
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        file_path = logs_dir / f'subsort_{timestamp}.log'
    
    try:
        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        if verbose:
            logger.info(f"Logging to file: {file_path}")
    
    except Exception as e:
        logger.warning(f"Could not create log file {file_path}: {e}")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a child logger with the given name"""
    return logging.getLogger(f'subsort.{name}')
