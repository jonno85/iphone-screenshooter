#!/bin/bash

# --- Functions ---
list_simulators() {
  echo "Available iOS Simulators:"
  xcrun simctl list devices available | grep -v "unavailable" | grep -E "Booted|Shutdown"
}

boot_simulator() {
  local udid=$1
  echo "Booting simulator $udid..."
  xcrun simctl boot "$udid"
  
  # Wait for simulator to fully boot
  echo "Waiting for simulator to boot..."
  until xcrun simctl list | grep "$udid" | grep -q "Booted"; do
    sleep 1
  done
  
  # Open Simulator.app to make the simulator visible
  echo "Opening Simulator.app..."
  open -a Simulator
  
  # Additional wait to ensure UI is ready
  sleep 5
}

# --- Main Script ---
# List available simulators
list_simulators

# Ask user to select a simulator
read -p "Enter simulator UDID (leave empty for default iPhone): " SIMULATOR_UDID

if [ -z "$SIMULATOR_UDID" ]; then
  # Try to find a booted iPhone simulator
  SIMULATOR_UDID=$(xcrun simctl list devices available | grep "iPhone" | grep "Booted" | head -1 | sed -E 's/.*\(([A-Za-z0-9-]+)\).*/\1/')
  
  # If no booted iPhone simulator, try to get any available iPhone
  if [ -z "$SIMULATOR_UDID" ]; then
    SIMULATOR_UDID=$(xcrun simctl list devices available | grep "iPhone" | grep "Shutdown" | head -1 | sed -E 's/.*\(([A-Za-z0-9-]+)\).*/\1/')
  fi
  
  if [ -z "$SIMULATOR_UDID" ]; then
    echo "No iPhone simulator found. Please create one in Xcode first."
    exit 1
  fi
  
  echo "Using simulator with UDID: $SIMULATOR_UDID"
fi

# Check if simulator is already booted
if ! xcrun simctl list | grep "$SIMULATOR_UDID" | grep -q "Booted"; then
  boot_simulator "$SIMULATOR_UDID"
else
  echo "Simulator is already booted."
  # Open Simulator.app to make sure it's visible
  open -a Simulator
fi

# Verify Maestro installation
if ! command -v maestro &> /dev/null; then
  echo "Maestro not found. Installing..."
  curl -Ls "https://get.maestro.mobile.dev" | bash
  source ~/.zshrc  # Or ~/.bashrc depending on your shell
fi

# Check Maestro version
echo "Maestro version:"
maestro --version

# List devices to verify simulator is detected by Maestro
echo "Checking if Maestro can detect the simulator..."
maestro devices

# Create a simple test flow if it doesn't exist
if [ ! -f "simple_test.yaml" ]; then
  echo "Creating a simple test flow..."
  cat > simple_test.yaml << EOL
appId: com.example.app  # Will be overridden by environment variable
---
- launchApp
- takeScreenshot: initial_screen
- tapOn:
    point: "50%,50%"
- takeScreenshot: after_tap
EOL
fi

# Ask for app bundle ID
read -p "Enter app bundle ID (e.g., com.example.myapp): " APP_BUNDLE_ID

if [ -z "$APP_BUNDLE_ID" ]; then
  echo "No bundle ID provided. Using Safari as default."
  APP_BUNDLE_ID="com.apple.mobilesafari"
fi

# Set environment variables for Maestro
export MAESTRO_APP_ID="$APP_BUNDLE_ID"

# Run Maestro test
echo "Running Maestro test for $APP_BUNDLE_ID on simulator $SIMULATOR_UDID..."
maestro test --target ios.simulator://$SIMULATOR_UDID simple_test.yaml

echo "Test completed."