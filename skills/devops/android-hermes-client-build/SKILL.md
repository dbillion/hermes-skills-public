---
name: android-hermes-client-build
description: Build Hermes Android client (hermes-relay).
version: 1.0.0
---
# Android Hermes Client Build (hermes-relay)

Build the Hermes Atlas Android-native mobile client. The upstream repo for the
Android use case (#02 "Hermes in your pocket") is **hermes-relay**
(Codename-11/hermes-relay) — chat, terminal, and device control over WSS.
Build it as a **sideload** debug APK (no Play account needed).

## Pre-flight (host)
- Android Studio + SDK usually already present on this box. Find them:
  `ls /opt/android-studio`, `ls /opt/android-sdk`, `ls ~/Android/Sdk`.
- Tool binaries live UNDER the SDK dirs, not on PATH:
  `/opt/android-sdk/cmdline-tools/latest/bin/sdkmanager`,
  `<sdk>/platform-tools/adb`. Export `ANDROID_HOME`/`ANDROID_SDK_ROOT` and call
  sdkmanager by absolute path.
- **Writable SDK dir matters.** `/opt/android-sdk` is often root-owned →
  `sdkmanager --licenses` / install fail with Permission denied on the
  `licenses/` dir. Use the **user-owned** SDK (`~/Android/Sdk`) instead and
  point `local.properties` `sdk.dir` at it.
- Java: repo uses Gradle toolchain JDK 17 (compile) + JDK 21 (tests, via foojay
  auto-provision). Studio's bundled JBR is fine; system `java` (21) also works.

## Step 1 — accept licenses + install compileSdk (INTERACTIVE — hand to user)
`sdkmanager` prompts `Accept? (y/N):` on stdin and the agent CANNOT answer it
reliably (piped `y`/`printf` is frequently ignored for the platform license).
This is the #1 reason an agent build stalls. **Give the user the command to run
in their own terminal; do not try to drive it.**

```bash
export ANDROID_HOME=$HOME/Android/Sdk ANDROID_SDK_ROOT=$HOME/Android/Sdk
/opt/android-sdk/cmdline-tools/latest/bin/sdkmanager "platforms;android-37.0"
# when it prints "Accept? (y/N):"  -> type y + Enter
```
The repo (`app/build.gradle.kts`) pins `compileSdk = 37`. Adjust the version to
match the repo if it has changed. `build-tools;36.1` is usually already present.

## Step 2 — point the repo at the SDK (write local.properties)
`local.properties` is gitignored and absent by default. Create it (non-destructive):
```
sdk.dir=/home/deeone/Android/Sdk
```
Use the **writable** SDK path from pre-flight, not /opt/android-sdk.

## Step 3 — build the sideload debug APK
```bash
cd <repo>/hermes-ecosystem-staging/02/hermes-relay
./gradlew assembleSideloadDebug
```
- Flavor choice: `sideload` declares the full Device-Control surface and
  installs without a Play account (recommended). `googlePlay` is the Play-track
  build. `release` needs a keystore (defer unless the user supplies one).
- First build auto-downloads Gradle 9.7, JDK toolchains, and many remote deps
  (JitPack sherpa-onnx, ML Kit, Coil, etc.) — slow, needs network.
- Output APK:
  `app/build/outputs/apk/sideload/debug/hermes-relay-<version>-sideload-debug.apk`

## Step 4 — install (optional, only if a phone is connected)
NOT included in a normal build approval — confirm with the user first.
```bash
~/Android/Sdk/platform-tools/adb install -r app/build/outputs/apk/sideload/debug/*.apk
```
If no device is connected, just hand the user the APK path to side-load.

## Pitfalls
- `./gradlew` exists and is executable in the repo; it self-bootstraps Gradle.
- If Gradle complains about AGP/JDK mismatch, the repo pins AGP 9.3.1 / Kotlin
  2.4.10 / Gradle 9.7 — let Gradle's toolchain resolver fetch the right JDK;
  don't force a system JAVA_HOME that's too old.
- `local.properties` with a root-owned `/opt/android-sdk` path will fail to
  resolve the platform even after you installed it elsewhere. Keep the
  `sdk.dir` and the installed-platform SDK the SAME directory.

## References
- `references/hermes-relay-build-notes.md` — exact commands run this session,
  repo layout, and the license-handoff transcript that confirmed the agent
  cannot satisfy the interactive prompt.
