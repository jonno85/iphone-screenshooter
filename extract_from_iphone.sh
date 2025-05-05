#!/bin/bash

echo "=== Extracting Apps from Connected iPhone ==="
echo ""

# Check if Apple Configurator 2 is installed
if ! [ -d "/Applications/Apple Configurator.app" ]; then
  echo "Apple Configurator 2 is not installed."
  echo "Please install it from the Mac App Store first."
  exit 1
fi

echo "1. Connect your iPhone to your Mac with a USB cable"
echo "2. Trust the computer on your iPhone if prompted"
echo "3. Open Apple Configurator 2"
echo ""
echo "Would you like to open Apple Configurator 2 now? (y/n)"
read -r open_choice

if [[ "$open_choice" == "y" || "$open_choice" == "Y" ]]; then
  open -a "Apple Configurator 2"
fi

echo ""
echo "In Apple Configurator 2:"
echo "1. Select your connected iPhone"
echo "2. Click on 'Apps' in the top menu"
echo "3. Right-click on the app you want to extract"
echo "4. Select 'Export' to save the .ipa file to your Mac"
echo ""
echo "The exported .ipa file can then be extracted to get the .app file for simulator installation."