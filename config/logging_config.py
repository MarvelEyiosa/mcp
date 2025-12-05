"""
Centralized logging configuration for MCP Server System
"""
import sys
from pathlib import Path
from loguru import logger
from config.settings import settings


def setup_logging():
    """Configure logging for the entire application"""
    
    # Remove default handler
    logger.remove()
    
    # Console handler
    logger.add(
        sys.stdout,
        format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True,
    )
    
    # File handler - all logs
    log_file = settings.LOG_DIR / "app.log"
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.LOG_LEVEL,
        rotation="500 MB",
        retention="10 days",
    )
    
    # File handler - errors only
    error_log_file = settings.LOG_DIR / "errors.log"
    logger.add(
        error_log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="500 MB",
        retention="30 days",
    )
    
    return logger


# Initialize logger
log = setup_logging()
