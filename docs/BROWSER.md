# Browser integration

## Local installation

1. Install the Windows desktop application using Setup.exe.
2. Extract the release `BrowserExtension.zip` to a permanent folder, or use the source repository's `browser-extension/` folder.
3. Open `chrome://extensions` or `edge://extensions`.
4. Enable **Developer mode**, choose **Load unpacked**, and select the folder containing `manifest.json`.
5. Open Halab. In the extension popup, enable automatic capture and click **Check connection**.

For an update, replace the files in the same directory and press **Reload ⟳** on the extension card. If the browser requests new permissions, review and approve them. Do not load multiple copies of the connector.

Chrome/Chromium **129+** is required by the published manifest. Windows Chrome normally disables sideloaded CRX packages that are not installed through its store. The supplied signed CRX is a package artifact, not a guarantee of local activation. Use developer mode for local testing. Public store distribution requires a separate store submission, review and approved listing; none is claimed here.

Official references: [loading unpacked](https://developer.chrome.com/docs/extensions/get-started/tutorial/hello-world#load-unpacked), [distribution](https://developer.chrome.com/docs/extensions/how-to/distribute), [disabled extensions](https://support.google.com/chrome_webstore/answer/2811969).

## Capture and bypass

- Known file navigations use declarative redirect rules before the browser requests the file.
- Attachment/file response headers can identify extensionless URLs and redirect them before the browser download manager starts.
- Other eligible HTTP(S) download items are retained durably, immediately cancelled/erased in the browser, and handed to the desktop. A tiny captured browser copy that finishes first is removed only through its exact download ID.
- The extension controls the browser download UI while automatic capture is enabled. It does not clear unrelated download history.
- **Alt + click** creates a temporary tab-scoped exception for one browser download; it is consumed when that download begins and expires if unused.
- If Halab is unavailable, use **Retry pending** in the popup. There is no automatic browser fallback. The redirect page also has an explicit **Use browser** button.

Direct capture requires HTTP(S) links. Blob/data URLs, POST request replay, authenticated sessions, DRM and arbitrary website-specific behavior are not universally supported. Private-window behavior has not been comprehensively validated; the generic download-item handler skips incognito items, but content/declarative capture can still run if you allow the extension in incognito.

## Native messaging and identity

The installer writes Chrome, Edge and Chromium native-host registrations under the installing user's `HKCU` registry. The host name is:

```text
com.mahmudabbas.halab
```

The deployed `com.mahmudabbas.halab.json` allows only the extension origin matching the committed public key. Developer-mode loading retains this ID:

```text
ckpkkojhhiamkbgihmnbpjfgpnbfjmkm
```

The native executable exchanges length-prefixed JSON with the browser and authenticated messages with the desktop over loopback. It does not run arbitrary commands supplied by web pages.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| CRX is disabled and cannot be enabled | Use **Load unpacked**; a local CRX signature is not Chrome Web Store approval. |
| Connection check fails | Re-run Setup.exe for the current Windows account, reload the extension, and ensure its ID matches the native manifest. |
| Another manager captures the file | Disable browser capture in that manager while using Halab. |
| Changes do not appear | Reload the extension card and refresh the website tab. |
| URL remains pending | Open Halab and use **Retry pending**; examine the popup error. |
| Video formats are unavailable | Install optional video support; only formats actually returned for a supported public URL are offered. |
| Resume fails | The server may reject ranges, the file may have changed or the URL may have expired; existing partial data is preserved rather than silently combined with another resource. |

The installer does not register Firefox integration, and no Firefox package is supplied.
