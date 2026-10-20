# Privacy

Copyright © 2026 Mahmud Abbas.

Halab Download Manager does not operate a developer-controlled download server or analytics endpoint. Downloads contact the websites selected by the user.

## Desktop storage

The application stores queue URLs, destination paths, status, schedules, settings and video selections in the current user's Qt local-app-data directory, normally `%LOCALAPPDATA%\Mahmud Abbas\HalabDownloadManager`. Temporary `.halab.part*` files and checkpoint metadata are written near the download destination. The connector uses a random token in local app data for loopback communication.

Closing the window keeps the program running in the tray. Exit from the tray menu to stop it. The installer registers current-user startup. Uninstalling keeps downloaded files and app-data history/settings.

## Browser storage and permissions

- HTTP(S) host access: detect matching download links and video elements.
- `declarativeNetRequestWithHostAccess`: redirect matching file navigations and attachment responses.
- `downloads` / `downloads.ui`: manage captured download items and the browser download UI, including an explicitly bypassed download.
- `nativeMessaging`: communicate with the installed Halab native host.
- `storage`: capture preferences, pending/failed URLs, errors and temporary bypass information.
- `contextMenus`: the explicit Download with Halab command.
- `alarms`: expiry of temporary bypass rules.

Successful handoffs remove matching pending URLs. Failed URLs can remain locally until retried or extension storage is cleared. Browser extension removal clears its extension storage according to browser behavior.

The extension does not request browser cookies or browsing-history permissions and does not extract account credentials. Download history access is used only for capture/cleanup. The generic download-item handler excludes incognito items; if you explicitly enable the extension in incognito, content scripts and declarative rules can still process matching navigations. Private-window integration is not claimed to be fully validated.

## Optional upstream video tools

The installer downloads optional tools from their official GitHub release locations after SHA-256 verification. yt-dlp contacts supported source sites; Node.js runs extraction JavaScript locally. FFmpeg is launched as a separate process for supported media operations. No DRM bypass is supplied. These dependencies and the browser have their own privacy practices and licenses.

The native host accepts supported operations and HTTP(S) URLs, with a configured extension-origin allowlist. The loopback token is intended to prevent unauthenticated local requests; it is not a defense against a malicious process already running as the same Windows user.
