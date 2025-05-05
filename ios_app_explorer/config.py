"""
Configuration settings for the iOS App Explorer
"""

# Device configuration
DEVICE_UDID = '00008120-001608CE3C72201E'
WDA_BUNDLE_ID = 'com.jonno.WebDriverAgentRunner'
WDA_PORT = 8101

# App list to explore
APP_LIST = [
    {
        'name': 'solflare',
        'bundleId': 'com.solflare.mobile',
        'ipaPath': '/path/to/AppSolflare.ipa'
    },
    {
        'name': 'galxe',
        'bundleId': 'com.galxe.app',
        'ipaPath': '/path/to/AppGalxe.ipa'
    },
    # Add more apps as needed
]

# Output directories
SCREENSHOT_DIR = './iphone_screenshots'
LOG_DIR = './logs'

# Exploration settings
MAX_DEPTH = 1
MAX_BUTTONS_PER_LEVEL = 15
MAX_SCROLLS = 3
WAIT_AFTER_CLICK = 1.0
WAIT_AFTER_LAUNCH = 2.0