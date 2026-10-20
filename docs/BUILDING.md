# Building Halab Download Manager

[English overview](../README.md) · [الشرح بالعربية](../README.ar.md)

## Tested toolchain

- Windows x64; the development/test machine used Windows 11.
- Qt **6.10.1 MinGW x64**, matching **MinGW 13.1** compiler/runtime.
- CMake 3.21 or later and Ninja.
- Python **3.10+** for packaging and integration tests.
- Node.js **24.x**; the published runtime is **24.18.0**.
- Inno Setup **6** for an installer. The script uses its modern download/archive APIs.
- Python `cryptography` only when creating a newly signed CRX.

Qt can be obtained from [Qt downloads](https://www.qt.io/download). Other upstream tools: [CMake](https://cmake.org/download/), [Ninja](https://ninja-build.org/), [Python](https://www.python.org/downloads/windows/), [Node.js](https://nodejs.org/en/download), [Inno Setup](https://jrsoftware.org/isdl.php). Follow their respective license terms. No SDK, compiler, private key or temporary browser profile is committed here.

## Build the desktop application

Open PowerShell in the repository root:

```powershell
.\scripts\build.ps1 -Python python
```

Defaults match a Qt installation under `C:\Qt`. Override them when needed:

```powershell
.\scripts\build.ps1 `
  -QtRoot C:\Qt\6.10.1\mingw_64 `
  -MingwBin C:\Qt\Tools\mingw1310_64\bin `
  -CMake C:\Qt\Tools\CMake_64\bin\cmake.exe `
  -NinjaBin C:\Qt\Tools\Ninja `
  -NodeExe 'C:\Program Files\nodejs\node.exe' `
  -Python python
```

Outputs:

- `build/bin/`: compiled desktop and native-host executables.
- `build/package/App/`: deployable Qt application with compiler/runtime DLLs, plugins, dependency licenses, the native-host manifest and Node.js.
- `dist/*-BrowserExtension.zip`: developer-mode extension package.
- `dist/SHA256SUMS.txt`: checksums of generated assets.

Run `build/package/App/HalabDownloadManager.exe`. Merely compiling does **not** register native messaging, startup or uninstall entries; the installer performs that step. Browser connection testing therefore needs an installed application or the isolated end-to-end test runner.

### Direct CMake alternative

Set the matching compiler and Ninja on `PATH`, then:

```powershell
cmake -S . -B build -G Ninja -DCMAKE_PREFIX_PATH=C:/Qt/6.10.1/mingw_64 -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel 4
```

This compiles executables but does not deploy the Qt/compiler DLLs. Use `scripts/build.ps1` to create the complete runtime folder.

## Extension packaging and signing

Developer mode does not require a private signing key:

```powershell
python .\scripts\package-extension.py
```

It creates a ZIP with `manifest.json` at the archive root. You can also load `browser-extension/` directly.

To reuse the existing signed package when rebuilding this release:

```powershell
python .\scripts\package-extension.py --crx C:\Downloads\HalabDownloadManager-1.0.3-BrowserExtension.crx
```

The supplied CRX must match the source manifest version and public key. Its signature is checked by the browser when installed; release asset checksums are published separately.

A maintainer with the matching private RSA key can create CRX3:

```powershell
python -m pip install cryptography
python .\scripts\package-extension.py --key C:\PrivateKeys\halab-extension.pem
```

**Private keys are never included in this repository or release assets.** The packaging script refuses a key stored inside the repository. The `key` field in `browser-extension/manifest.json` is a **public** key and is deliberately committed so loading the unpacked extension preserves its ID:

```text
ckpkkojhhiamkbgihmnbpjfgpnbfjmkm
```

For a different signing key, update both `browser-extension/manifest.json` (`key`) and `installer/com.mahmudabbas.halab.json` (`allowed_origins`) to the new public key/extension ID before building. Do not publish the private key. A modified extension can be tested unpacked without the original signing key.

## Create Setup.exe

Download the matching CRX from the release, install Inno Setup, then:

```powershell
.\scripts\build.ps1 -CreateInstaller -BrowserCrx C:\Downloads\HalabDownloadManager-1.0.3-BrowserExtension.crx
```

Alternatively, use `-ExtensionKey C:\PrivateKeys\halab-extension.pem` to sign from source. Override `-InnoCompiler` if `ISCC.exe` is installed elsewhere.

The installer source is `installer/Setup.iss`. It:

- Installs under `{commonpf32}\Halab Download Manager` (normally `C:\Program Files (x86)\Halab Download Manager`).
- Requires administrator permission, creates shortcuts and an uninstaller.
- Registers the native host for Chrome, Edge and Chromium in the installing user's registry.
- Registers that user's Windows startup command with `--background`.
- Offers optional yt-dlp and FFmpeg downloads with pinned SHA-256 verification.

The installer does not silently enable extensions in Chrome. Do not add machine policies to bypass normal browser approval. See [BROWSER.md](BROWSER.md).

The source tree, test scripts and development tooling are **not** installed with the application. Runtime dependency license files are retained.

## Tests

```powershell
.\scripts\test.ps1 -Python python -Node node
```

Tests use generated files, temporary app data and local HTTP servers. They verify resume across process restarts, a real TCP disconnect, SHA-256/ZIP integrity, filename detection, overwrite prevention, deletion confirmation, lifecycle, languages and extension behavior. Local firewall/sandbox rules must permit loopback traffic for these tests.

`tests/bridge_test.py` additionally needs the optional video tools in the tested application. After installing them into a test installation, set `HALAB_TEST_APP` to that application folder before running it directly. Do not point destructive experiments at personal download folders.

For real browser/native messaging tests:

```powershell
.\scripts\test-browser.ps1 -BrowserExe 'C:\Tools\chrome-win64\chrome.exe' -Python python -Node node
```

Use official [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/). The runner creates a disposable browser profile and temporary native-host registry entry, then removes its own registry entry. It does not use your normal browser profile. A running competing download manager can interfere with tests; disable its capture or use an isolated test browser binary.

## Editing and versioning

- `src/main.cpp`: desktop window, queue, settings and transfer implementation.
- `src/download_names.h`: safe filenames, MIME/signature handling and collisions.
- `src/media_transfer.inc`, `src/video_dialog.inc`, `src/halab_tools.h`: optional video processes and format UI.
- `src/native_host.cpp`: framed browser native messaging and authenticated loopback handoff.
- `src/languages.json`, `src/localization.h`: translations and layout direction.
- `browser-extension/`: extension interception, UI and content scripts.

Keep `VERSION`, both CMake project versions, `src/halab.rc`, the displayed About/native-host version, `browser-extension/manifest.json`, and `installer/Setup.iss` consistent when making a release. Update the installer download URLs/hashes if upstream dependencies change, and update dependency notices when upgrading bundled runtimes.
