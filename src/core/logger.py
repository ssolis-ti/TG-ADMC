
import sys
import logging
from loguru import logger

class InterceptHandler(logging.Handler):
    """
    Redirects standard logging messages to Loguru.
    """
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def setup_logging():
    """
    Configures Loguru to replace standard logging handlers.
    """
    # Remove all existing handlers
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(logging.INFO)

    # Remove every other logger's handlers and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True
        
    # Configure Loguru
    logger.configure(handlers=[{
        "sink": sys.stdout,
        "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        "colorize": True,
        "enqueue": True
    }])

    logger.info("CORE: Logging System Initialized (High Precision Mode)")

# Alias for compatibility with existing modules
app_logger = logger
