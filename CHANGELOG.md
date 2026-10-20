# Changelog

## 1.0.3

- Added declarative interception for common file navigations and attachment/file response headers.
- Added explicit one-download Alt bypass and retained pending requests without automatic browser fallback.
- Improved HTTP resume discovery when ETag, Accept-Ranges or HEAD support is missing; added Last-Modified, overlap verification, legacy checkpoint migration and changed-resource protection.
- Added deletion confirmation and an opt-in checkbox for deleting the selected downloaded file from disk.
- Validated resume with real TCP interruption and byte-level checks; validated browser/native messaging with an isolated Chrome for Testing profile.
- Published organized source, bilingual documentation, build/test helpers and release assets.

## 1.0.2

- Added Windows autostart, tray icon, background operation and window reopening.
- Fixed reentrant table/selection updates during download deletion.
- Improved direct-link handoff and scoped browser history cleanup.

## 1.0.1

- Added the Windows setup wizard and CRX3 packaging.
- Set the default install location to Program Files (x86).
- Simplified branding/About and separated development files from installed runtime files.

## 1.0.0

- Initial C++/Qt desktop manager, translations, HTTP engine and browser/native connector.
