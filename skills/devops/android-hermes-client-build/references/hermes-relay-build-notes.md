# hermes-relay build — session notes (2026-08-15)

## Repo layout (already cloned)
- Path: `/home/deeone/hermes-ecosystem-staging/02/hermes-relay`
- Git: `main` @ `0d6c3bd` ("Merge pull request #346 from Codename-11/dev")
- Gradle modules: `:app`, `:relay-core`, `:relay-ui`, `:ui-preview`, `quest` (included build)
- `gradlew` present, executable, self-bootstraps Gradle 9.7.0

## Build config pins (app/build.gradle.kts)
- `compileSdk = 37`, `targetSdk = 36`, `minSdk = 26`
- AGP `9.3.1`, Kotlin `2.4.10`, compose-bom `2026.06.01`
- Flavors: `googlePlay` (canonical Play install, `com.axiomlabs.hermesrelay`)
  and `sideload` (adds `.sideload` suffix; declares full Device-Control surface).
- Toolchains: compile JDK 17, tests on JDK 21 via foojay resolver.
- Release signing reads `HERMES_KEYSTORE_*` env or `local.properties`
  `hermes.keystore.*`; falls back to debug signing if absent.

## SDK toolchain on this box
- `/opt/android-studio` present (root-owned install).
- `/opt/android-sdk` = ROOT-OWNED → cannot write `licenses/` as `deeone`.
- `/home/deeone/Android/Sdk` = user-writable (use this one).
- sdkmanager absolute path used: `/opt/android-sdk/cmdline-tools/latest/bin/sdkmanager`
- Installed platforms found: only `android-36`. Needed `android-37.0` → install.
- build-tools `36.1` present; gradle wrapper `gradle-9.7.0-bin.zip`.
- `adb` at `/home/deeone/Android/Sdk/platform-tools/adb`.

## THE LICENSE HANDOFF (why the agent stalls)
`sdkmanager "platforms;android-37.0"` prints:

    ...January 16, 2019
    ---------------------------------------
    Accept? (y/N): Skipping following packages as the license is not accepted:
    Android SDK Platform 37.0
    The following packages can not be installed since their licenses ... were not accepted:
      platforms;android-37.0

Attempts that FAILED to satisfy it:
- Writing `licenses/android-sdk-license` with the generic 3-hash file → rejected
  (platform 37 uses a *different* accepted-hash than the generic one).
- `printf 'y\n...' | sdkmanager ...` → the prompt consumed nothing; still "Skipping".
- Piping `yes | sdkmanager --licenses` separately DID write the accepted hashes
  into `~/Android/Sdk/licenses/` (android-sdk-license got the real 3 hashes),
  but the *platform install* re-prompted and still hung.

CONCLUSION: the agent cannot reliably drive the interactive `Accept? (y/N):`
for the platform license. The robust path is to hand the user the command and
let them type `y`. The user confirmed this with "give me the command to start".

## Working command sequence given to the user (Step 1, interactive)
    export ANDROID_HOME=$HOME/Android/Sdk ANDROID_SDK_ROOT=$HOME/Android/Sdk
    /opt/android-sdk/cmdline-tools/latest/bin/sdkmanager "platforms;android-37.0"
    # type y at the Accept? prompt

## local.properties written (Step 2)
    sdk.dir=/home/deeone/Android/Sdk

## Build + APK output (Step 3, not yet run to completion in session)
    cd /home/deeone/hermes-ecosystem-staging/02/hermes-relay
    ./gradlew assembleSideloadDebug
    # APK: app/build/outputs/apk/sideload/debug/hermes-relay-<ver>-sideload-debug.apk

## Status at session end
- MeiGen MCP (#09) verified working; meigen config corrected via `hermes mcp add`
  (the prior `hermes config set` had stringified args/env — see mcp-server-management).
- hermes-relay: SDK 37 install + assembleDebug were handed to the user as
  interactive steps (license prompt). Build NOT completed by the agent.
- #02 (Hermes in your pocket) remains "implemented/repo present" but APK not yet
  produced at session close — pending the user's license accept + gradle build.
