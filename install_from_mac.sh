#!/bin/bash

# List available simulators
echo "Available iOS Simulators:"
xcrun simctl list devices available | grep -v "unavailable" | grep -E "Booted|Shutdown"

# Ask user to select a simulator
read -p "Enter simulator UDID: " SIMULATOR_UDID

if [ -z "$SIMULATOR_UDID" ]; then
  echo "No simulator UDID provided. Exiting."
  exit 1
fi

# Boot simulator if needed
if ! xcrun simctl list | grep "$SIMULATOR_UDID" | grep -q "Booted"; then
  echo "Booting simulator $SIMULATOR_UDID..."
  xcrun simctl boot "$SIMULATOR_UDID"
  
  # Wait for simulator to boot
  until xcrun simctl list | grep "$SIMULATOR_UDID" | grep -q "Booted"; do
    sleep 1
  done
  
  # Open Simulator.app to make it visible
  open -a Simulator
fi

echo "There are several ways to install apps from your Mac to the simulator:"
echo "1. Install from .app file (extracted from .ipa or built from Xcode)"
echo "2. Install from Mac App Store app (requires extraction)"
echo "3. Install from .ipa file (requires extraction)"
read -p "Choose an option (1-3): " OPTION

case $OPTION in
  1)
    read -p "Enter path to .app file: " APP_PATH
    if [ ! -d "$APP_PATH" ]; then
      echo "App path does not exist or is not a directory."
      exit 1
    fi
    
    echo "Installing app from $APP_PATH to simulator $SIMULATOR_UDID..."
    xcrun simctl install "$SIMULATOR_UDID" "$APP_PATH"
    ;;
    
  2)
    echo "To install from Mac App Store app, you need to:"
    echo "1. Find the app in ~/Library/Group Containers/K36BKF7T3D.group.com.apple.configurator/Library/Caches/Assets/TemporaryItems/MobileApps/"
    echo "2. Right-click on the .ipa file and select 'Show Package Contents'"
    echo "3. Navigate to Payload folder and find the .app file"
    echo "4. Copy the .app file to a location on your Mac"
    
    read -p "Enter path to extracted .app file: " APP_PATH
    if [ ! -d "$APP_PATH" ]; then
      echo "App path does not exist or is not a directory."
      exit 1
    fi
    
    echo "Installing app from $APP_PATH to simulator $SIMULATOR_UDID..."
    xcrun simctl install "$SIMULATOR_UDID" "$APP_PATH"
    ;;
    
  3)
    read -p "Enter path to .ipa file: " IPA_PATH
    if [ ! -f "$IPA_PATH" ]; then
      echo "IPA file does not exist."
      exit 1
    fi
    
    # Create temporary directory
    TEMP_DIR=$(mktemp -d)
    echo "Extracting IPA to $TEMP_DIR..."
    
    # Unzip IPA
    unzip -q "$IPA_PATH" -d "$TEMP_DIR"
    
    # Find .app file
    APP_PATH=$(find "$TEMP_DIR/Payload" -name "*.app" -type d | head -1)
    
    if [ -z "$APP_PATH" ]; then
      echo "Could not find .app file in IPA."
      rm -rf "$TEMP_DIR"
      exit 1
    fi
    
    echo "Found app at $APP_PATH"
    echo "Installing app to simulator $SIMULATOR_UDID..."
    xcrun simctl install "$SIMULATOR_UDID" "$APP_PATH"
    
    # Clean up
    rm -rf "$TEMP_DIR"
    ;;
    
  *)
    echo "Invalid option."
    exit 1
    ;;
esac

# Check if installation was successful
if [ $? -eq 0 ]; then
  echo "App installed successfully."
  
  # Try to extract bundle ID
  if [ -n "$APP_PATH" ] && [ -d "$APP_PATH" ]; then
    BUNDLE_ID=$(defaults read "$APP_PATH/Info" CFBundleIdentifier 2>/dev/null)
    
    if [ -n "$BUNDLE_ID" ]; then
      echo "Detected bundle ID: $BUNDLE_ID"
      read -p "Launch the app now? (y/n): " LAUNCH
      
      if [[ "$LAUNCH" == "y" || "$LAUNCH" == "Y" ]]; then
        echo "Launching app..."
        xcrun simctl launch "$SIMULATOR_UDID" "$BUNDLE_ID"
      fi
    fi
  fi
else
  echo "Failed to install app."
fi