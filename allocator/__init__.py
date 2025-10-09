"""
Allocator package for clustering and routing optimization.
"""

import logging
import sys


def setup_logging(level=logging.INFO):
    """
    Set up logging configuration for the allocator package.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Get root logger for allocator package
    logger = logging.getLogger('allocator')
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def get_logger(name):
    """
    Get a logger instance for a specific module.

    Args:
        name: Module name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(f'allocator.{name}')


# Set up default logging
setup_logging()
