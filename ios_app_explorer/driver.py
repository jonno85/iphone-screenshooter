"""
Appium driver setup and management
"""
import logging
from appium import webdriver
from appium.options.ios import XCUITestOptions
from ios_app_explorer.config import DEVICE_UDID, WDA_BUNDLE_ID, WDA_PORT

def get_appium_options(app_info):
    """
    Configure Appium options for iOS testing
    
    Args:
        app_info: Dictionary containing app information
        
    Returns:
        Configured XCUITestOptions
    """
    options = XCUITestOptions()
    options.show_xcode_log = True
    options.platform_name = "iOS"
    options.device_name = "iPhone"
    options.udid = DEVICE_UDID
    options.automation_name = "XCUITest"
    options.bundle_id = app_info['bundleId']
    options.no_reset = True
    options.wda_local_port = WDA_PORT
    options.wda_bundle_id = WDA_BUNDLE_ID
    logging.debug(f"Appium options configured for {app_info['name']}")
    return options

def create_driver(app_info):
    """
    Create and initialize Appium driver
    
    Args:
        app_info: Dictionary containing app information
        
    Returns:
        Initialized Appium driver or None if failed
    """
    try:
        logging.info("Connecting to Appium server")
        options = get_appium_options(app_info)
        driver = webdriver.Remote('http://localhost:4723', options=options)
        driver.implicitly_wait(5)
        logging.info("Successfully connected to Appium server")
        return driver
    except Exception as e:
        logging.error(f"Failed to create driver: {e}")
        return None