# BOUNTY Dex

Modern Android-to-Windows desktop companion inspired by Samsung DeX.

## Project status
Prototype source code. This repository currently contains the Windows desktop controller and setup documentation. It does **not** yet contain signed/installable Windows or Android binaries.

## Windows 10/11 prototype
The desktop app uses ADB + scrcpy to mirror and control an Android phone. It supports USB and ADB-over-Wi-Fi.

### Requirements
- Windows 10 or 11
- Python 3.10+
- Android Platform Tools (ADB)
- scrcpy for Windows (include the complete extracted scrcpy folder)

### Setup
1. Install Python 3.10+.
2. Download Android SDK Platform Tools and extract them into `tools/platform-tools/`.
3. Download the Windows release of scrcpy and extract its complete contents into `tools/scrcpy/`.
4. Open this folder in File Explorer, type `cmd` in the address bar, then run:
   `py -3 -m pip install -r requirements.txt`
5. Run `run-windows.bat`.

### USB connection
1. On Android, enable Developer options and USB debugging.
2. Connect the phone using a data-capable USB cable.
3. Accept the RSA debugging prompt on the phone.
4. In BOUNTY Dex, refresh devices and choose Connect USB.

### Wi-Fi connection
1. Initially connect by USB and accept the debugging prompt.
2. Make sure the phone and PC are on the same Wi-Fi network.
3. Find the phone's local IP address in Android Wi-Fi settings.
4. Enter the IP in BOUNTY Dex and choose Connect Wi-Fi.
5. The app switches ADB to TCP port 5555 and starts scrcpy.

For newer Android versions, wireless debugging pairing may be required; the prototype's simple TCP/IP method is intended for devices that permit ADB TCP/IP mode.

## Android companion
The Android companion APK is a separate deliverable and is not included as a binary yet. The initial mirroring/control path uses Android's built-in USB debugging authorization and scrcpy. A companion app can later provide pairing guidance, connection status and settings.

## Important limitations of prototype 0.1
- The mirrored phone appears in a separate scrcpy window, not embedded in the BOUNTY Dex desktop shell.
- This is screen mirroring and remote input, not a full Samsung DeX environment.
- App streaming behavior depends on the Android device, Android version and OEM restrictions.
- Never accept ADB authorization prompts on computers you do not trust.

## Roadmap
- 0.1: Windows controller, USB/Wi-Fi ADB, screen mirroring and mouse/keyboard control.
- 0.2: Embedded mirror window and connection diagnostics.
- 0.3: File transfer, clipboard and desktop shell improvements.
- 1.0: Packaged Windows installer and Android companion APK.
