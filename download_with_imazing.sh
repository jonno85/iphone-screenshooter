#!/bin/bash

echo "=== Downloading iPhone Apps Using iMazing ==="
echo ""

# Check if iMazing is installed
if ! [ -d "/Applications/iMazing.app" ]; then
  echo "iMazing is not installed."
  echo "Would you like to open the website to download it? (y/n)"
  read -r install_choice
  
  if [[ "$install_choice" == "y" || "$install_choice" == "Y" ]]; then
    echo "Opening iMazing website..."
    open "https://imazing.com/download"
    echo "Please install iMazing and run this script again."
  else
    echo "You can download iMazing from https://imazing.com/download later."
  fi
  exit 1
fi

echo "iMazing is installed."
echo ""
echo "To download iPhone apps using iMazing:"
echo "1. Open iMazing"
echo "2. Connect your iPhone or use a virtual device"
echo "3. Select your device in the sidebar"
echo "4. Click on 'Apps' in the main panel"
echo "5. Click 'Manage Apps' in the toolbar"
echo "6. Click 'Library' tab to see your purchased apps"
echo "7. Download the apps you want"
echo ""
echo "Would you like to open iMazing now? (y/n)"
read -r open_choice

if [[ "$open_choice" == "y" || "$open_choice" == "Y" ]]; then
  echo "Opening iMazing..."
  open -a iMazing
fi