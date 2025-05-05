#!/bin/bash

echo "=== Downloading iPhone Apps Using Apple Configurator 2 ==="
echo ""

# Check if Apple Configurator 2 is installed
if ! [ -d "/Applications/Apple Configurator.app" ]; then
  echo "Apple Configurator 2 is not installed."
  echo "Would you like to open the Mac App Store to download it? (y/n)"
  read -r install_choice
  
  if [[ "$install_choice" == "y" || "$install_choice" == "Y" ]]; then
    echo "Opening Mac App Store..."
    open "macappstore://itunes.apple.com/app/id1037126344"
    echo "Please install Apple Configurator 2 and run this script again."
  else
    echo "You can download Apple Configurator 2 from the Mac App Store later."
  fi
  exit 1
fi

echo "Apple Configurator 2 is installed."
echo ""
echo "To download iPhone apps using Apple Configurator 2:"
echo "1. Open Apple Configurator 2"
echo "2. Sign in with your Apple ID (Apps > Account)"
echo "3. Click on 'Apps' in the top menu"
echo "4. Search for and download the app you want"
echo ""
echo "Downloaded apps will be stored in:"
echo "~/Library/Group Containers/K36BKF7T3D.group.com.apple.configurator/Library/Caches/Assets/TemporaryItems/MobileApps/"
echo ""
echo "Would you like to open Apple Configurator 2 now? (y/n)"
read -r open_choice

if [[ "$open_choice" == "y" || "$open_choice" == "Y" ]]; then
  echo "Opening Apple Configurator 2..."
  open -a "Apple Configurator 2"
  
  # Wait for user to download apps
  echo ""
  echo "After downloading apps, press Enter to continue..."
  read -r
  
  # Check if apps were downloaded
  APP_DIR="$HOME/Library/Group Containers/K36BKF7T3D.group.com.apple.configurator/Library/Caches/Assets/TemporaryItems/MobileApps/"
  
  if [ -d "$APP_DIR" ]; then
    echo "Checking for downloaded apps..."
    IPA_COUNT=$(find "$APP_DIR" -name "*.ipa" | wc -l | xargs)
    
    if [ "$IPA_COUNT" -gt 0 ]; then
      echo "Found $IPA_COUNT .ipa files in the downloads folder."
      echo "Would you like to see the list of downloaded apps? (y/n)"
      read -r list_choice
      
      if [[ "$list_choice" == "y" || "$list_choice" == "Y" ]]; then
        echo "Downloaded apps:"
        find "$APP_DIR" -name "*.ipa" -exec basename {} \;
        
        echo ""
        echo "Would you like to open the downloads folder? (y/n)"
        read -r folder_choice
        
        if [[ "$folder_choice" == "y" || "$folder_choice" == "Y" ]]; then
          open "$APP_DIR"
        fi
      fi
    else
      echo "No .ipa files found in the downloads folder."
      echo "Make sure you've downloaded apps in Apple Configurator 2."
    fi
  else
    echo "Downloads folder not found. Make sure you've downloaded apps in Apple Configurator 2."
  fi
fi