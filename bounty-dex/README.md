# BOUNTY Dex

BOUNTY Dex has two separate downloads: a Windows desktop app and an Android companion app.

## Downloads

After GitHub Actions finishes successfully, both installers are published in the **[BOUNTY Dex Releases](https://github.com/black1011f-bot/bounty-gaming-website./releases/tag/bounty-dex-latest)** page:

- **Windows 10/11:** `BOUNTY-Dex-Windows.zip` — portable desktop app with BOUNTY-Dex.exe, Android Platform Tools (ADB), and the complete Windows scrcpy folder with runtime files.
- **Android:** `BOUNTY-Dex-Android.apk` — installable companion app with illustrated USB and Wi-Fi setup instructions.

The Windows ZIP is checked to be at least 50 MiB. It is not padded with dummy data; it contains the actual desktop app and bundled tools.

## Install on Windows

1. Open the [Releases page](https://github.com/black1011f-bot/bounty-gaming-website./releases/tag/bounty-dex-latest).
2. Download `BOUNTY-Dex-Windows.zip`.
3. Extract the whole ZIP to a normal folder.
4. Open the extracted `BOUNTY-Dex` folder and run `BOUNTY-Dex.exe`.

## Install on Android

1. Open the [Releases page](https://github.com/black1011f-bot/bounty-gaming-website./releases/tag/bounty-dex-latest) on your phone.
2. Download `BOUNTY-Dex-Android.apk`.
3. Open the downloaded APK and allow installation from this source if Android asks.
4. Launch **BOUNTY Dex** from the app list.

The Android app is the phone-side companion and illustrated setup guide. The actual screen mirroring and desktop controls are performed by the Windows app.

## Connect a Samsung phone

1. Enable Developer options by tapping **Build number** seven times in Settings → About phone → Software information.
2. In Developer options, enable **USB debugging**.
3. Connect the phone to the PC with a data-capable USB cable and accept the RSA authorization prompt on the phone.
4. Open BOUNTY Dex on Windows, press **Refresh**, select the phone, then press **Mirror USB**.

For Wi-Fi, the phone and PC must be on the same network.

- **USB-to-Wi-Fi:** connect by USB, select the phone, enter its IPv4 address, and press **Подключить по Wi-Fi**. The app switches ADB to TCP/IP port 5555.
- **Android 11+ Wireless debugging:** on the phone open Developer options → Wireless debugging → Pair device with pairing code. In BOUNTY Dex enter the pairing IP:port and six-digit code, then press **Сопрячь Wi-Fi**. Next enter the phone IP in the main Wi-Fi field, press **Подключить по Wi-Fi**, and enter the separate connection port shown on the Wireless debugging screen. The pairing port and connection port are different.

## Features

- USB ADB device detection
- ADB-over-Wi-Fi for devices that permit TCP/IP mode
- Launcher-app listing, search and launch
- Live screen streaming and mouse/keyboard control via scrcpy
- Landscape / portrait display rotation controls for the PC mirror
- Stream resolution presets (720p, 1280p, 1600p, 1920p) and 30/45/60 FPS limits
- Clipboard synchronization and keep-awake while streaming
- Dark interface and illustrated Russian setup guide

## Important limitations

BOUNTY Dex currently provides live screen mirroring and remote input; it is **not** a full Samsung DeX replacement. The orientation selector rotates the mirrored image on the PC. It cannot force an Android app that does not support landscape mode to redesign its interface. Use Alt+R in the scrcpy window to request a device orientation switch; the foreground app may refuse it. Resolution presets limit the stream size while preserving the phone's aspect ratio. For a low-powered PC, start with 720p and 30 FPS. The mirrored phone screen opens in a separate scrcpy window. Android apps continue running on the phone; this app cannot force every Android app into desktop/freeform windows. Do not authorize ADB access on a computer you do not trust.

## Build from source

Windows requirements: Windows 10/11 and Python 3.10+.

```powershell
cd bounty-dex/windows
py -3 -m pip install -r requirements.txt
py -3 bounty_dex.py
```
