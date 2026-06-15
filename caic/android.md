# Android App

Go Mode is the Android app for caic. It is a native shell that hosts the caic web frontend in a WebView and adds native capabilities the browser cannot provide: voice, notifications, screenshot capture, and Halo glasses management. You get the full caic web experience plus hands-free control from your phone.

### Task list

All running agents at a glance. See prompt, branch, status, cost, and CI results for each task.

<img src="/screenshots/android-task-list.avif" alt="Android task list" style="max-width: 300px">

### Task detail

Follow an agent's work in real time: streamed text, tool uses, and results. Send follow-up messages, push branches, or stop the agent.

<img src="/screenshots/android-task-detail.avif" alt="Android task detail" style="max-width: 300px">

## First launch

On first launch, Go Mode shows a native settings screen. Enter the service URL of your caic instance, for example `https://caic.example.com`, and the app loads its web frontend. A persistent native header bar stays available so you can reopen settings and switch instances at any time.

## Native features

- **Voice**: supervise and control tasks hands-free. See [Voice](./voice) for setup.
- **Notifications**: receive hosted-service notifications when an agent finishes a turn or needs input.
- **Screenshot capture**: capture the screen when a task needs a visual.
- **Passkeys**: WebAuthn passkey sign-in works inside the WebView.
- **Halo glasses**: manage Brilliant Labs Halo devices over Bluetooth (see below).

## Halo glasses

Go Mode manages [Brilliant Labs Halo](https://www.brilliant.xyz/) glasses over Bluetooth Low Energy. From the Halo screen you can:

- Scan for nearby Halo devices
- Connect to or disconnect from a device
- Toggle auto-connect so the app reconnects to your chosen device automatically

## Prerequisites

1. [Android SDK](https://developer.android.com/studio) with build-tools and platform for API 36
2. USB debugging enabled: **Settings → Developer options → USB debugging**
3. Phone connected via USB and authorized (`adb devices` shows your device)

## Build and install

```bash
# Build, install, and start Go Mode on the connected device:
make android-push-gomode
```
