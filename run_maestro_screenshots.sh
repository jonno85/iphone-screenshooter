#!/bin/bash

# --- Configuration ---
# Define apps: AppName=BundleID
APPS=()
APPS+=("galxe:com.galxe.app")
APPS+=("chrome:com.google.chrome.ios")
# Add more apps here: APPS+=("newapp:com.new.app")

SCREENSHOT_BASE_DIR="./maestro_iphone_screenshots" # Output directory
MAIN_FLOW_FILE="simple_test.yaml"                 # Using the simpler test file

# --- Main Loop ---
echo "Starting Maestro screenshot process..."
mkdir -p "$SCREENSHOT_BASE_DIR"

# Check if Maestro is installed
if ! command -v maestro &> /dev/null; then
    echo "Error: Maestro CLI not found. Please install it with:"
    echo "curl -Ls \"https://get.maestro.mobile.dev\" | bash"
    exit 1
fi

# Print Maestro version for debugging
maestro --version

for app_entry in "${APPS[@]}"; do
  # Split the entry by colon
  name=$(echo "$app_entry" | cut -d':' -f1)
  id=$(echo "$app_entry" | cut -d':' -f2)
  
  echo "--- Processing App: $name ($id) ---"

  # Set environment variables for Maestro to use inside the flow
  export MAESTRO_APP_ID="$id"
  export APP_NAME="$name" # Optional: Useful if you need the name inside the flow

  # Define where Maestro should output screenshots for this app
  APP_SCREENSHOT_DIR="$SCREENSHOT_BASE_DIR/$name"
  mkdir -p "$APP_SCREENSHOT_DIR"

  # Run Maestro test for this app
  echo "Running Maestro test..."
  maestro test "$MAIN_FLOW_FILE" --output "$APP_SCREENSHOT_DIR/maestro_output"

  if [ $? -ne 0 ]; then
      echo "!!! Maestro execution failed for $name !!!"
  fi

  echo "Finished processing $name. Output in $APP_SCREENSHOT_DIR"
  echo ""
  sleep 2 # Small pause between apps
done

echo "All apps processed."
