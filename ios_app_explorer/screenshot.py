"""
Main module for capturing iOS app screenshots
"""
import os
import time
import logging
from time import sleep
from ios_app_explorer.config import APP_LIST, SCREENSHOT_DIR, WAIT_AFTER_LAUNCH
from ios_app_explorer.logger import setup_logging
from ios_app_explorer.driver import create_driver
from ios_app_explorer.navigation import navigate_and_capture_screenshots, restart_app

def create_folders(app_data):
    """
    Create necessary folders for screenshots
    
    Args:
        app_data: App information dictionary
        
    Returns:
        Path to the app's screenshot directory
    """
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR)
        logging.debug(f"Created main screenshot directory: {SCREENSHOT_DIR}")
        
    app_screenshot_dir = os.path.join(SCREENSHOT_DIR, app_data['name'])
    if not os.path.exists(app_screenshot_dir):
        os.makedirs(app_screenshot_dir)
        logging.debug(f"Created app screenshot directory: {app_screenshot_dir}")

    return app_screenshot_dir

def take_app_screenshots(app_info):
    """
    Capture screenshots for a single app
    
    Args:
        app_info: App information dictionary
    """
    # Set up logging for this app
    setup_logging(app_info['name'])
    logging.info(f"Starting screenshot capture for {app_info['name']}")
    
    # Create screenshot directory
    app_screenshot_dir = create_folders(app_info)
    
    # Create driver
    driver = None
    try:
        driver = create_driver(app_info)
        if not driver:
            logging.error("Failed to create driver, skipping app")
            return
            
        # Wait for app to fully load
        sleep(WAIT_AFTER_LAUNCH)
        
        # Take initial screenshot
        initial_screenshot_path = os.path.join(app_screenshot_dir, f"{app_info['name']}_initial.png")
        driver.save_screenshot(initial_screenshot_path)
        logging.info(f"Saved initial screenshot to {initial_screenshot_path}")
        
        # Try basic back navigation test
        try:
            driver.back()
            sleep(1.5)
            
            back_screenshot_path = os.path.join(app_screenshot_dir, f"{app_info['name']}_back.png")
            driver.save_screenshot(back_screenshot_path)
            logging.info(f"Saved back button screenshot to {back_screenshot_path}")
            
            # Restart app to ensure we're in a clean state
            restart_app(driver, app_info)
        except Exception as e:
            logging.warning(f"Back button test failed: {e}")
        
        # Start the main navigation and screenshot capture
        start_time = time.time()
        
        navigate_and_capture_screenshots(
            driver=driver, 
            app_info=app_info, 
            path=app_screenshot_dir
        )

        elapsed_time = time.time() - start_time
        logging.info(f"Finished screenshots for {app_info['name']} in {elapsed_time:.1f} seconds")

    except Exception as e:
        logging.error(f"Error processing {app_info['name']}: {e}", exc_info=True)
    finally:
        if driver:
            logging.info("Quitting driver")
            driver.quit()
        sleep(2)

def main():
    """
    Main function to process all apps
    """
    # Set up initial logging
    setup_logging()
    logging.info("Starting iOS app screenshot capture script")
    
    # Validate configuration
    if not APP_LIST:
        logging.error("No apps configured in APP_LIST. Please add at least one app.")
        return
        
    # Process each app
    logging.info(f"Processing {len(APP_LIST)} apps")
    for app_data in APP_LIST:
        logging.info(f"Processing app: {app_data['name']}")
        take_app_screenshots(app_data)
    
    logging.info("Screenshot capture completed for all apps")

if __name__ == '__main__':
    main()