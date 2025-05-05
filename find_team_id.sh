#!/bin/bash

echo "=== Finding Your Apple Developer Team ID ==="
echo ""

# Method 1: Check from Xcode
echo "Method 1: Find Team ID from Xcode"
echo "1. Open Xcode"
echo "2. Go to Xcode > Preferences (or Xcode > Settings in newer versions)"
echo "3. Click on the 'Accounts' tab"
echo "4. Select your Apple ID on the left"
echo "5. Click on 'Manage Certificates...' button"
echo "6. Your Team ID appears in parentheses next to your team name"
echo ""

# Method 2: Check from Developer Portal
echo "Method 2: Find Team ID from Apple Developer Portal"
echo "1. Visit https://developer.apple.com/account/"
echo "2. Sign in with your Apple ID"
echo "3. Click on 'Membership' in the left sidebar"
echo "4. Your Team ID is listed under 'Team ID'"
echo ""

# Method 3: Check from existing provisioning profile
echo "Method 3: Find Team ID from existing provisioning profile"
echo "If you have any provisioning profiles installed, you can extract the Team ID:"
echo ""

PROFILES_DIR="$HOME/Library/MobileDevice/Provisioning Profiles"
if [ -d "$PROFILES_DIR" ]; then
  echo "Checking for provisioning profiles..."
  PROFILE_COUNT=$(ls "$PROFILES_DIR"/*.mobileprovision 2>/dev/null | wc -l | xargs)
  
  if [ "$PROFILE_COUNT" -gt 0 ]; then
    echo "Found $PROFILE_COUNT provisioning profile(s)."
    echo "Extracting Team ID from the first profile:"
    
    FIRST_PROFILE=$(ls "$PROFILES_DIR"/*.mobileprovision | head -1)
    
    # Extract and decode the profile
    TEAM_ID=$(security cms -D -i "$FIRST_PROFILE" | grep -A1 TeamIdentifier | grep string | sed -e 's/<string>//' -e 's/<\/string>//' -e 's/^[[:space:]]*//')
    
    if [ -n "$TEAM_ID" ]; then
      echo "Your Team ID appears to be: $TEAM_ID"
      echo ""
      echo "To use this Team ID in your Appium script, replace 'YOUR_TEAM_ID' with:"
      echo "'$TEAM_ID'"
    else
      echo "Could not extract Team ID from the profile."
    fi
  else
    echo "No provisioning profiles found in $PROFILES_DIR"
  fi
else
  echo "Provisioning profiles directory not found."
fi

# Method 4: Check from keychain
echo ""
echo "Method 4: Find Team ID from developer certificate in Keychain"
echo "If you have a developer certificate installed, you can extract the Team ID:"
echo ""

# Look for developer certificates
CERT_INFO=$(security find-certificate -a -c "iPhone Developer" -p | grep "OU=" | grep "^subject" | head -1)

if [ -n "$CERT_INFO" ]; then
  # Extract the OU field which contains the Team ID
  TEAM_ID=$(echo "$CERT_INFO" | sed -n 's/.*OU=\([A-Z0-9]*\).*/\1/p')
  
  if [ -n "$TEAM_ID" ]; then
    echo "Your Team ID appears to be: $TEAM_ID"
    echo ""
    echo "To use this Team ID in your Appium script, replace 'YOUR_TEAM_ID' with:"
    echo "'$TEAM_ID'"
  else
    echo "Could not extract Team ID from certificate."
  fi
else
  echo "No developer certificates found in Keychain."
fi

echo ""
echo "Once you have your Team ID, update your Appium script with:"
echo "'appium:xcodeOrgId': '$TEAM_ID'  // Replace with your actual Team ID"