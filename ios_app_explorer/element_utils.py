"""
Utilities for working with UI elements
"""
import logging
import json
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains

def is_element_clickable(element):
    """
    Check if an element is likely to be clickable based on its attributes and type
    
    Args:
        element: WebElement to check
        
    Returns:
        Boolean indicating if element appears to be clickable
    """
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
    """
    Try different methods to interact with an element with stale element handling
    
    Args:
        element: WebElement to click
        driver: Appium driver
        
    Returns:
        Boolean indicating if click was successful
    """
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
    """
    Find all potentially clickable elements on the screen
    
    Args:
        driver: Appium driver
        buttons: Optional existing buttons dictionary to append to
        level: Current exploration depth level
        
    Returns:
        Dictionary of button elements with metadata
    """
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
        logging.error(f"Error in fetch_all_buttons: {e}")
        return {}