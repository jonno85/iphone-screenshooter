"""
Navigation and screen exploration utilities
"""
import os
import logging
from time import sleep
from ios_app_explorer.element_utils import fetch_all_buttons, try_click_element
from ios_app_explorer.scroll_utils import capture_scrolled_screenshots
from ios_app_explorer.config import MAX_DEPTH, MAX_BUTTONS_PER_LEVEL, WAIT_AFTER_CLICK

def try_go_back(driver, app_info):
    """
    Try different methods to go back to the previous screen
    
    Args:
        driver: Appium driver
        app_info: App information dictionary
        
    Returns:
        Boolean indicating if back navigation was successful
    """
    try:
        driver.back()
        sleep(1)
        return True
    except Exception:
        pass
    
    try:
        close_buttons = fetch_all_buttons(driver)
        close_buttons = [b for b in close_buttons.values() if b['is_close_button']]
        if close_buttons:
            try_click_element(close_buttons[0]['btn'], driver)
            sleep(1)
            return True
    except Exception:
        pass
    
    try:
        nav_bars = driver.find_elements(by='class name', value='XCUIElementTypeNavigationBar')
        if nav_bars:
            for nav_bar in nav_bars:
                try:
                    buttons = nav_bar.find_elements(by='class name', value='XCUIElementTypeButton')
                    if buttons:
                        try_click_element(buttons[0], driver)
                        sleep(1)
                        return True
                except Exception:
                    continue
    except Exception:
        pass
    
    logging.warning("All back navigation methods failed")
    return False

def navigate_and_capture_screenshots(driver, app_info, path, level=0, buttons=None, visited_screens=None, max_per_level=None):
    """
    Navigate through the app and capture screenshots
    
    Args:
        driver: Appium driver
        app_info: App information dictionary
        path: Path to save screenshots
        level: Current exploration depth level
        buttons: Optional existing buttons dictionary
        visited_screens: Set of visited screen signatures
        max_per_level: Maximum number of buttons to try per level
    """
    if max_per_level is None:
        max_per_level = MAX_BUTTONS_PER_LEVEL
        
    if visited_screens is None:
        visited_screens = set()
    
    # Generate a signature for the current screen to avoid revisiting
    screen_signature = hash(driver.page_source)
    if screen_signature in visited_screens:
        logging.debug("Screen already visited, skipping")
        return
    
    visited_screens.add(screen_signature)
    logging.info(f"Exploring screen {len(visited_screens)} at level {level}")
    
    # Take regular screenshot
    screenshot_path = os.path.join(path, f"{app_info['name']}_{level}_{len(visited_screens)}.png")
    driver.save_screenshot(screenshot_path)
    logging.info(f"Saved screenshot to {screenshot_path}")
    
    # Take scrolled screenshots if the screen is scrollable
    base_name = f"{app_info['name']}_{level}_{len(visited_screens)}"
    capture_scrolled_screenshots(driver, app_info, path, base_name)
    
    # Check if we've reached the maximum depth
    if level >= MAX_DEPTH:
        logging.debug(f"Reached maximum depth level {level}, stopping exploration")
        return
    
    # Find all clickable elements on the screen
    driver.implicitly_wait(3)
    logging.debug("Fetching all buttons on screen")
    buttons = fetch_all_buttons(driver=driver, buttons=None, level=level)
    
    # Filter for clickable buttons
    clickable_buttons = [b for b in buttons.values() 
                        if b['enabled'] and b['visible'] and b['clickable']]
    
    # Separate tab buttons from other buttons
    tab_buttons = [b for b in clickable_buttons if b.get('is_tab_item', False)]
    other_buttons = [b for b in clickable_buttons 
                    if not b.get('is_tab_item', False) and not b['is_close_button']]
    
    all_buttons = tab_buttons + other_buttons
    
    logging.info(f"Found {len(all_buttons)} clickable buttons ({len(tab_buttons)} tabs, {len(other_buttons)} other)")
    
    # Sort buttons by priority (buttons with text are more interesting)
    def button_priority(btn):
        has_text = bool(btn['text'] or btn['name'] or btn['label'])
        is_button_type = btn['type'] == 'XCUIElementTypeButton'
        return (has_text, is_button_type)
    
    other_buttons.sort(key=button_priority, reverse=True)
    
    # Limit the number of buttons to try
    max_buttons_to_try = min(max_per_level, len(all_buttons))
    logging.info(f"Will try clicking on {max_buttons_to_try} buttons")
    
    # Try clicking each button and explore resulting screens
    for i, button_data in enumerate(all_buttons[:max_buttons_to_try]):
        button_name = button_data['name'] or button_data['text'] or button_data['label'] or f"Button {i+1}"
        logging.info(f"Attempting to click button {i+1}/{max_buttons_to_try}: {button_name}")
        
        try:
            # Store the state before clicking
            before_click = driver.page_source
            
            try:
                # Try to find a fresh reference to the element
                fresh_element = None
                if button_data['name']:
                    try:
                        fresh_element = driver.find_element(by='accessibility id', value=button_data['name'])
                        logging.debug(f"Found element by accessibility id: {button_data['name']}")
                    except Exception as e:
                        logging.debug(f"Could not find element by accessibility id: {e}")
                
                if not fresh_element and button_data['label']:
                    try:
                        xpath = f"//{button_data['type']}[@label='{button_data['label']}']"
                        fresh_element = driver.find_element(by='xpath', value=xpath)
                        logging.debug(f"Found element by xpath: {xpath}")
                    except Exception as e:
                        logging.debug(f"Could not find element by xpath: {e}")
                
                if not fresh_element:
                    logging.debug("Using original button reference")
                    fresh_element = button_data['btn']
                
                # Try to click the element
                success = try_click_element(fresh_element, driver)
            except Exception as e:
                logging.warning(f"Error finding fresh element, using original: {e}")
                success = try_click_element(button_data['btn'], driver)
            
            if success:
                logging.info(f"Successfully clicked button: {button_name}")
                sleep(WAIT_AFTER_CLICK)
                
                # Check if the screen changed after clicking
                after_click = driver.page_source
                if before_click == after_click:
                    logging.debug("Screen did not change after click, continuing")
                    continue
                
                # If we have a new screen, take a screenshot and explore it
                new_screen_signature = hash(after_click)
                if new_screen_signature not in visited_screens:
                    visited_screens.add(new_screen_signature)
                    safe_button_name = ''.join(c if c.isalnum() else '_' for c in button_name)[:20]
                    new_screenshot_path = os.path.join(
                        path, 
                        f"{app_info['name']}_{level+1}_{len(visited_screens)}_{safe_button_name}.png"
                    )
                    driver.save_screenshot(new_screenshot_path)
                    logging.info(f"Saved new screen screenshot to {new_screenshot_path}")
                    
                    # Recursively explore the new screen
                    if level < MAX_DEPTH - 1:
                        navigate_and_capture_screenshots(
                            driver=driver,
                            app_info=app_info,
                            path=path,
                            level=level+1,
                            visited_screens=visited_screens,
                            max_per_level=max_per_level
                        )
                
                # Try to go back to the previous screen
                logging.debug("Attempting to go back")
                if not try_go_back(driver, app_info):
                    logging.warning("Failed to go back, breaking exploration")
                    break
                
                # Verify we're back at the original screen
                current = driver.page_source
                if hash(current) != hash(before_click):
                    logging.warning("Could not return to previous screen, restarting app")
                    driver.terminate_app(app_info['bundleId'])
                    sleep(1)
                    driver.activate_app(app_info['bundleId'])
                    sleep(2)
        except Exception as e:
            logging.error(f"Error clicking button: {e}")
            try:
                logging.info("Restarting app after error")
                driver.terminate_app(app_info['bundleId'])
                sleep(1)
                driver.activate_app(app_info['bundleId'])
                sleep(2)
            except Exception as restart_error:
                logging.error(f"Failed to restart app: {restart_error}")

def restart_app(driver, app_info):
    """
    Restart the app to return to a known state
    
    Args:
        driver: Appium driver
        app_info: App information dictionary
        
    Returns:
        Boolean indicating if restart was successful
    """
    try:
        logging.info(f"Restarting app: {app_info['name']}")
        driver.terminate_app(app_info['bundleId'])
        sleep(1)
        driver.activate_app(app_info['bundleId'])
        sleep(2)
        return True
    except Exception as e:
        logging.error(f"Failed to restart app: {e}")
        return False
