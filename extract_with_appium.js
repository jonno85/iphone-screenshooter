const { remote } = require('webdriverio');

async function extractAppFromDevice() {
  // Connect to the device
  const caps = {
    platformName: 'iOS',
    'appium:deviceName': 'iPhone',
    'appium:automationName': 'XCUITest',
    'appium:udid': 'AUTO', // Will detect connected device
    'appium:xcodeOrgId': 'NB8WWTRV6R', // Required for real devices
    'appium:xcodeSigningId': 'iPhone Developer'
  };

  const driver = await remote({
    protocol: 'http',
    hostname: 'localhost',
    port: 4723,
    path: '/wd/hub',
    capabilities: caps
  });

  // Get the app container path (requires bundle ID)
  const bundleId = 'com.galxe.app'; // Replace with actual bundle ID
  
  try {
    // Pull the app binary
    // Note: This requires a jailbroken device or special entitlements
    const appData = await driver.pullFile(`@${bundleId}:app/`);
    
    // Save the app data to a file
    const fs = require('fs');
    fs.writeFileSync('/path/to/save/app.ipa', Buffer.from(appData, 'base64'));
    
    console.log('App extracted successfully');
  } catch (err) {
    console.error('Failed to extract app:', err);
  }
  
  await driver.deleteSession();
}

extractAppFromDevice().catch(console.error);