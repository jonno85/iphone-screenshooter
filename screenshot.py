import os
import time
import logging
from datetime import datetime
from appium import webdriver
from appium.options.ios import XCUITestOptions
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains

# --- Configure Logging ---
def setup_logging(app_name=None):
    """Configure logging to both console and file"""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Generate log filename with timestamp and app name if provided
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f"logs/appium_{'_' + app_name if app_name else ''}_{timestamp}.log"
    
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

# --- Configuration ---
APP_LIST = [
    {'name': 'solflare', 'bundleId': 'com.solflare.mobile', 'ipaPath': '/path/to/AppSolflare.ipa'},
    # Add more apps as needed
]
DEVICE_UDID = '00008120-001608CE3C72201E'
SCREENSHOT_DIR = './iphone_screenshots'
WDA_BUNDLE_ID = 'com.jonno.WebDriverAgentRunner'


def get_appium_options(app_info):
    options = XCUITestOptions()
    options.show_xcode_log = True
    options.platform_name = "iOS"
    options.device_name = "iPhone"
    options.udid = DEVICE_UDID
    options.automation_name = "XCUITest"
    options.bundle_id = app_info['bundleId']
    options.no_reset = True
    options.wda_local_port = 8101
    options.wda_bundle_id = WDA_BUNDLE_ID
    logging.debug(f"Appium options configured for {app_info['name']}")
    return options


def is_element_clickable(element):
    """Check if an element is likely to be clickable based on its attributes and type"""
    try:
        element_type = element.get_attribute('type')
        is_enabled = element.is_enabled()
        is_displayed = element.is_displayed()
        
        clickable_types = [
            'XCUIElementTypeButton',
            'XCUIElementTypeLink',
            'XCUIElementTypeCell'
        ]
        
        name = element.get_attribute('name') or ''
        label = element.get_attribute('label') or ''
        
        interactive_keywords = ['tap', 'click', 'press', 'select', 'choose', 'open']
        might_be_interactive = any(keyword in (name + label).lower() for keyword in interactive_keywords)
        
        return (is_enabled and is_displayed and 
                (element_type in clickable_types or might_be_interactive))
    except Exception as e:
        logging.error(f"Error checking clickability: {e}")
        return False


def try_click_element(element, driver):
    """Try different methods to interact with an element with stale element handling"""
    try:
        element_type = element.get_attribute('type')
        element_name = element.get_attribute('name') or ''
        element_label = element.get_attribute('label') or ''
        logging.info(f"Clicking element - Type: {element_type}, Name: {element_name}, Label: {element_label}")
        
        # Standard click
        element.click()
        return True
    except Exception as e1:
        if "StaleElementReferenceError" in str(e1):
            logging.warning("Element is stale (no longer in DOM)")
            return False
            
        logging.debug(f"Standard click failed: {e1}")
        try:
            # Try ActionChains tap
            actions = ActionChains(driver)
            actions.move_to_element(element).tap().perform()
            return True
        except Exception as e2:
            if "StaleElementReferenceError" in str(e2):
                return False
                
            try:
                # Try JavaScript click
                driver.execute_script("arguments[0].click();", element)
                return True
            except Exception as e3:
                try:
                    # Try tap by coordinates
                    rect = element.rect
                    x = rect['x'] + (rect['width'] / 2)
                    y = rect['y'] + (rect['height'] / 2)
                    driver.tap([(x, y)])
                    return True
                except Exception:
                    return False


def fetch_all_buttons(driver, buttons=None, level=0):
    buttons = {} if buttons is None else buttons

    element_types = [
        'XCUIElementTypeButton',
        'XCUIElementTypeCell',
        'XCUIElementTypeLink',
        'XCUIElementTypeImage',
        'XCUIElementTypeStaticText',
        'XCUIElementTypeOther',
        'XCUIElementTypeNavigationBar'
    ]
    
    interactive_keywords = [
        'tap', 'click', 'press', 'select', 'choose', 'open', 
        'swap', 'stake', 'send', 'receive', 'buy', 'sell',
        'add', 'remove', 'create', 'delete', 'edit', 'view',
        'menu', 'settings', 'profile', 'account', 'wallet',
        'home', 'back', 'next', 'done', 'cancel', 'confirm'
    ]
    
    try:
        for element_type in element_types:
            try:
                driver.implicitly_wait(2)
                elements = driver.find_elements(by='class name', value=element_type) or []
                
                for btn in elements:
                    try:
                        element_uid = btn.get_attribute('UID') or str(hash(btn))
                        if element_uid in buttons:
                            continue
                        
                        try:
                            if not btn.is_displayed():
                                continue
                        except:
                            continue
                        
                        name = btn.get_attribute('name') or ''
                        label = btn.get_attribute('label') or ''
                        text = btn.text or ''
                        is_visible = True
                        
                        try:
                            is_enabled = bool(btn.is_enabled())
                        except:
                            is_enabled = False
                        
                        element_text = (name + label + text).lower()
                        has_interactive_keyword = any(keyword in element_text for keyword in interactive_keywords)
                        
                        rect_str = btn.get_attribute('rect')
                        is_likely_tab_item = False
                        try:
                            if rect_str:
                                import json
                                rect = json.loads(rect_str)
                                if rect.get('y', 0) > 250 and rect.get('height', 0) > 40:
                                    is_likely_tab_item = True
                        except Exception:
                            pass
                        
                        is_clickable = (
                            is_visible and is_enabled and (
                                element_type in ['XCUIElementTypeButton', 'XCUIElementTypeLink', 'XCUIElementTypeCell'] or
                                (element_type == 'XCUIElementTypeStaticText' and (
                                    has_interactive_keyword or is_likely_tab_item
                                )) or
                                has_interactive_keyword
                            )
                        )
                        
                        is_close_button = any(
                            close_text in element_text
                            for close_text in ['close', 'dismiss', '×', 'x', 'cancel', 'back']
                        )
                        
                        buttons[element_uid] = {
                            'id': element_uid,
                            'text': text,
                            'name': name,
                            'label': label,
                            'visible': is_visible,
                            'enabled': is_enabled,
                            'clickable': is_clickable,
                            'btn': btn,
                            'is_close_button': is_close_button,
                            'type': element_type,
                            'is_tab_item': is_likely_tab_item
                        }
                    except Exception:
                        continue
            except Exception:
                continue
        
        return buttons
    
    except Exception as e:
        print(f"Error in fetch_all_buttons: {e}")
        return {}


def navigate_and_capture_screenshots(driver, app_info, path, level=0, buttons=None, visited_screens=None, max_per_level=5):
    if visited_screens is None:
        visited_screens = set()
    
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
    capture_scrolled_screenshots(driver, app_info, path, base_name, max_scrolls=3)
    
    if level >= 1:
        logging.debug(f"Reached maximum depth level {level}, stopping exploration")
        return
    
    driver.implicitly_wait(3)
    logging.debug("Fetching all buttons on screen")
    buttons = fetch_all_buttons(driver=driver, buttons=None, level=level)
    
    clickable_buttons = [b for b in buttons.values() 
                        if b['enabled'] and b['visible'] and b['clickable']]
    
    tab_buttons = [b for b in clickable_buttons if b.get('is_tab_item', False)]
    other_buttons = [b for b in clickable_buttons 
                    if not b.get('is_tab_item', False) and not b['is_close_button']]
    
    all_buttons = tab_buttons + other_buttons
    
    logging.info(f"Found {len(all_buttons)} clickable buttons ({len(tab_buttons)} tabs, {len(other_buttons)} other)")
    
    def button_priority(btn):
        has_text = bool(btn['text'] or btn['name'] or btn['label'])
        is_button_type = btn['type'] == 'XCUIElementTypeButton'
        return (has_text, is_button_type)
    
    other_buttons.sort(key=button_priority, reverse=True)
    
    max_buttons_to_try = min(max_per_level, len(all_buttons))
    logging.info(f"Will try clicking on {max_buttons_to_try} buttons")
    
    for i, button_data in enumerate(all_buttons[:max_buttons_to_try]):
        button_name = button_data['name'] or button_data['text'] or button_data['label'] or f"Button {i+1}"
        logging.info(f"Attempting to click button {i+1}/{max_buttons_to_try}: {button_name}")
        
        try:
            before_click = driver.page_source
            
            try:
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
                
                success = try_click_element(fresh_element, driver)
            except Exception as e:
                logging.warning(f"Error finding fresh element, using original: {e}")
                success = try_click_element(button_data['btn'], driver)
            
            if success:
                logging.info(f"Successfully clicked button: {button_name}")
                sleep(1.5)
                
                after_click = driver.page_source
                if before_click == after_click:
                    logging.debug("Screen did not change after click, continuing")
                    continue
                
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
                
                logging.debug("Attempting to go back")
                if not try_go_back(driver, app_info):
                    logging.warning("Failed to go back, breaking exploration")
                    break
                
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


def try_go_back(driver, app_info):
    """Try different methods to go back to the previous screen"""
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
    
    try:
        driver.terminate_app(app_info['bundleId'])
        sleep(1)
        driver.activate_app(app_info['bundleId'])
        sleep(2)
        return True
    except Exception:
        return False


def take_app_screenshots(app_info, path):
    # Set up logging for this app
    setup_logging(app_info['name'])
    logging.info(f"Starting screenshot capture for {app_info['name']}")
    
    options = get_appium_options(app_info)
    driver = None
    try:
        logging.info("Connecting to Appium server")
        driver = webdriver.Remote('http://localhost:4723', options=options)
        driver.implicitly_wait(5)

        sleep(2)
        
        initial_screenshot_path = os.path.join(path, f"{app_info['name']}_initial.png")
        driver.save_screenshot(initial_screenshot_path)
        logging.info(f"Saved initial screenshot to {initial_screenshot_path}")
        
        try:
            driver.back()
            sleep(1.5)
            
            back_screenshot_path = os.path.join(path, f"{app_info['name']}_back.png")
            driver.save_screenshot(back_screenshot_path)
            logging.info(f"Saved back button screenshot to {back_screenshot_path}")
            
            driver.terminate_app(app_info['bundleId'])
            sleep(1)
            driver.activate_app(app_info['bundleId'])
            sleep(2)
        except Exception as e:
            logging.warning(f"Back button test failed: {e}")
        
        max_runtime = 180
        start_time = time.time()
        
        navigate_and_capture_screenshots(
            driver=driver, 
            app_info=app_info, 
            path=path,
            max_per_level=15
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


def create_folders(app_data):
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR)
        logging.debug(f"Created main screenshot directory: {SCREENSHOT_DIR}")
        
    app_screenshot_dir = os.path.join(SCREENSHOT_DIR, app_data['name'])
    if not os.path.exists(app_screenshot_dir):
        os.makedirs(app_screenshot_dir)
        logging.debug(f"Created app screenshot directory: {app_screenshot_dir}")

    return app_screenshot_dir


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
    """Check if the current screen appears to be scrollable"""
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
                print(f"Unsupported locator type: {locator_type}")
                return None
            
            # If element is found and displayed, return it
            if element.is_displayed():
                return element
        except Exception:
            # Element not found, scroll down and try again
            scroll_screen(driver, 'down')
            sleep(1)
    
    # Element not found after max_swipes
    print(f"Element '{element_locator}' not found after {max_swipes} swipes")
    return None

if __name__ == '__main__':
    # Set up initial logging
    setup_logging()
    logging.info("Starting iOS app screenshot capture script")
    
    if DEVICE_UDID == 'YOUR_DEVICE_UDID':
        logging.error("Please replace 'YOUR_DEVICE_UDID' with your actual device UDID.")
    else:
        logging.info(f"Processing {len(APP_LIST)} apps on device {DEVICE_UDID}")
        for app_data in APP_LIST:
            logging.info(f"Processing app: {app_data['name']}")
            app_screenshot_dir = create_folders(app_data)
            take_app_screenshots(app_data, path=app_screenshot_dir)
        
        logging.info("Screenshot capture completed for all apps")
