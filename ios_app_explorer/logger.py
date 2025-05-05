"""
Logging configuration for the iOS App Explorer
"""
import os
import logging
from datetime import datetime
from ios_app_explorer.config import LOG_DIR

def setup_logging(app_name=None):
    """
    Configure logging to both console and file
    
    Args:
        app_name: Optional name of the app being explored
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    # Generate log filename with timestamp and app name if provided
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f"{LOG_DIR}/appium_{'_' + app_name if app_name else ''}_{timestamp}.log"
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers to avoid duplicates when function is called multiple times
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler with a higher log level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_format)
    
    # Create file handler which logs even debug messages
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    
    # Add the handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    logging.info(f"Logging initialized. Log file: {log_filename}")
    return logger