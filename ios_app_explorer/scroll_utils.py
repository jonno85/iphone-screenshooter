"""
Utilities for scrolling and capturing scrolled content
"""
import os
import logging
from time import sleep

def scroll_screen(driver, direction='down', percent=0.5):
    """
    Scroll the screen in the specified direction
    
    Args:
        driver: Appium driver
        direction: 'up', 'down', 'left', or 'right'
        percent: How much of the screen to scroll (0.0-1.0)
    
    Returns:
        True if scroll was successful, False otherwise
    """
    try:
        window_size = driver.get_window_size()
        width = window_size['width']
        height = window_size['height']
        
        # Calculate start and end points for the swipe
        if direction == 'down':
            start_x = width * 0.5
            start_y = height * 0.3
            end_x = width * 0.5
            end_y = height * (0.3 + percent)
        elif direction == 'up':
            start_x = width * 0.5
            start_y = height * 0.7
            end_x = width * 0.5
            end_y = height * (0.7 - percent)
        elif direction == 'right':
            start_x = width * 0.2
            start_y = height * 0.5
            end_x = width * (0.2 + percent)
            end_y = height * 0.5
        elif direction == 'left':
            start_x = width * 0.8
            start_y = height * 0.5
            end_x = width * (0.8 - percent)
            end_y = height * 0.5
        else:
            logging.error(f"Invalid direction: {direction}")
            return False
        
        # Execute the swipe
        logging.debug(f"Scrolling {direction} by {percent*100}% of screen")
        driver.swipe(start_x, start_y, end_x, end_y, 500)
        sleep(1)  # Wait for scroll animation to complete
        return True
    except Exception as e:
        logging.error(f"Error scrolling {direction}: {e}")
        return False

def is_scrollable(driver):
    """
    Check if the current screen appears to be scrollable
    
    Args:
        driver: Appium driver
        
    Returns:
        Boolean indicating if screen appears to be scrollable
    """
    try:
        # Look for scrollable elements
        scrollable_types = [
            'XCUIElementTypeScrollView',
            'XCUIElementTypeTable',
            'XCUIElementTypeCollectionView'
        ]
        
        for element_type in scrollable_types:
            elements = driver.find_elements(by='class name', value=element_type)
            if elements:
                logging.debug(f"Found scrollable element of type: {element_type}")
                return True
        
        logging.debug("No scrollable elements found on screen")
        return False
    except Exception as e:
        logging.error(f"Error checking if screen is scrollable: {e}")
        return False

def capture_scrolled_screenshots(driver, app_info, path, base_name, max_scrolls=3):
    """
    Scroll through a screen and capture screenshots at each position
    
    Args:
        driver: Appium driver
        app_info: App information dictionary
        path: Path to save screenshots
        base_name: Base name for the screenshot files
        max_scrolls: Maximum number of scrolls to perform
    """
    if not is_scrollable(driver):
        logging.info("Screen doesn't appear to be scrollable, skipping scroll captures")
        return
    
    # Take initial screenshot before scrolling
    initial_path = os.path.join(path, f"{base_name}_scroll_0.png")
    driver.save_screenshot(initial_path)
    logging.info(f"Saved initial scroll screenshot to {initial_path}")
    
    # Store page source to detect when content stops changing
    previous_source = driver.page_source
    
    # Scroll down and take screenshots
    for i in range(1, max_scrolls + 1):
        if scroll_screen(driver, 'down'):
            sleep(1)  # Wait for content to settle
            
            # Check if page content changed after scrolling
            current_source = driver.page_source
            if hash(current_source) == hash(previous_source):
                logging.info("Reached end of scrollable content")
                break
            
            previous_source = current_source
            
            # Take screenshot after scrolling
            scroll_path = os.path.join(path, f"{base_name}_scroll_{i}.png")
            driver.save_screenshot(scroll_path)
            logging.info(f"Saved scroll screenshot to {scroll_path}")
    
    # Scroll back to the top
    logging.debug("Scrolling back to the top")
    for _ in range(max_scrolls):
        scroll_screen(driver, 'up')

def scroll_to_element(driver, element_locator, locator_type='accessibility id', max_swipes=5):
    """
    Scroll until an element is visible
    
    Args:
        driver: Appium driver
        element_locator: The identifier to find the element
        locator_type: Type of locator (accessibility id, xpath, etc.)
        max_swipes: Maximum number of swipes to attempt
        
    Returns:
        The element if found, None otherwise
    """
    for i in range(max_swipes):
        try:
            # Try to find the element
            if locator_type == 'accessibility id':
                element = driver.find_element(by='accessibility id', value=element_locator)
            elif locator_type == 'xpath':
                element = driver.find_element(by='xpath', value=element_locator)
            elif locator_type == 'class name':
                element = driver.find_element(by='class name', value=element_locator)
            else:
                logging.error(f"Unsupported locator type: {locator_type}")
                return None
            
            # If element is found and displayed, return it
            if element.is_displayed():
                return element
        except Exception:
            # Element not found, scroll down and try again
            scroll_screen(driver, 'down')
            sleep(1)
    
    # Element not found after max_swipes
    logging.warning(f"Element '{element_locator}' not found after {max_swipes} swipes")
    return None