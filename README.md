## steps to install

```zsh
arch -arm64 brew install libimobiledevice ideviceinstaller usbmuxd

sudo npm install -g appium

appium driver install xcuitest 
```

## to get the device uuid
```zsh
idevice_id -l
```

## start the appium server
```zsh
appium server
```

## run the script

add the app package and name into the `APP_LIST` struct then
N.B. the app must be already installed on the device and in case logged in / configured

```zsh
uv run ios_app_explorer/main.py  
```


In Xcode, go to the menu bar: Window -> Devices and Simulators.

Key Commands:
- idevice_id -l: List connected device UDIDs.
- ideviceinstaller -i /path/to/YourApp.ipa: Install an app (requires .ipa file).
- ideviceinstaller -u <bundle_id>: Uninstall an app by its Bundle ID.
- idevicescreenshot /path/to/save/screenshot.png: Take a screenshot of the current screen.
- idevicedebug run <bundle_id>: Launch an app (can be a bit finicky, UI automation frameworks handle this better).
- ideviceinfo: Get various device details.