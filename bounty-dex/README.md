# BOUNTY Dex

Dark Apple-inspired Android-to-Windows companion for Samsung phones, including Galaxy A16.

## Windows package

The Windows release is distributed as a ZIP containing:
- BOUNTY-Dex.exe
- Android Platform Tools (ADB)
- The complete Windows scrcpy folder and its runtime DLLs

This avoids asking users to download ADB and scrcpy separately. The ZIP size is determined by the actual app and required tools; it is not artificially padded to reach a number.

## Install and run

1. Download the **BOUNTY-Dex-Windows** ZIP from the successful GitHub Actions run.
2. Extract the entire ZIP to a normal folder (do not run the EXE from inside the ZIP).
3. Start BOUNTY-Dex.exe.
4. On the phone, enable Developer options and USB debugging, connect by a data-capable USB cable, and accept the RSA prompt.
5. Press Refresh, select the phone, then press Mirror USB.

For Wi-Fi, first connect USB and enable ADB TCP/IP from the app. Enter the phone's IPv4 address and connect. Some newer Android versions require pairing through Android Wireless debugging first.

## Build from source

Requirements: Windows 10/11, Python 3.10+.

```powershell
cd bounty-dex/windows
py -3 -m pip install -r requirements.txt
py -3 bounty_dex.py
```

## Features

- USB ADB device detection
- ADB-over-Wi-Fi for devices that permit TCP/IP mode
- Launcher-app listing, search and launch
- Screen mirroring and mouse/keyboard control via scrcpy
- Illustrated Russian setup guide and dark SVG interface

## Limitations

This is screen mirroring and remote input, not a full Samsung DeX implementation. The scrcpy screen opens in its own window. Android apps are still running on the phone; BOUNTY Dex does not make every app run in desktop/freeform mode. ADB and scrcpy are included in the Windows ZIP build. Never authorize ADB access on a computer you do not trust.

## Android companion

The Android APK is a companion guide with illustrated USB/Wi-Fi setup instructions. It does not mirror the screen itself; the Windows application does that through ADB and scrcpy.
