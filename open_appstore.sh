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

# Check if simulator is booted
if ! xcrun simctl list | grep "$SIMULATOR_UDID" | grep -q "Booted"; then
  echo "Booting simulator $SIMULATOR_UDID..."
  xcrun simctl boot "$SIMULATOR_UDID"
  
  # Wait for simulator to boot
  until xcrun simctl list | grep "$SIMULATOR_UDID" | grep -q "Booted"; do
    sleep 1
  done
fi

# Open Simulator.app to make it visible
open -a Simulator

# Ask for app name to search
read -p "Enter app name to search in App Store: " APP_NAME

# URL encode the app name
ENCODED_APP_NAME=$(echo "$APP_NAME" | sed 's/ /%20/g')

# Open App Store with search query
echo "Opening App Store with search for '$APP_NAME'..."
xcrun simctl openurl "$SIMULATOR_UDID" "https://apps.apple.com/search?term=$ENCODED_APP_NAME"

echo "Please sign in if needed and download the app manually."