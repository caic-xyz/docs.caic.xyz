# Android App

Voice-first companion app to manage coding agents from your phone.

## Prerequisites

1. [Android SDK](https://developer.android.com/studio) with build-tools and platform for API 36
2. USB debugging enabled: **Settings → Developer options → USB debugging**
3. Phone connected via USB and authorized (`adb devices` shows your device)

## Build and install

```bash
# Build and install debug APK on connected device:
make android-push

# Build only (no install):
make android-build
```
