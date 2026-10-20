# Contributing / التعديل والمساهمة

See [LICENSE](LICENSE) before distributing modified versions. Public source availability does not automatically grant an open-source redistribution license. The project owner can authorize changes and contributions.

1. Clone the repository and install the toolchain in [BUILDING.md](docs/BUILDING.md).
2. Make a focused change in `src/`, `browser-extension/`, `installer/` or the translation catalog.
3. Rebuild with `scripts/build.ps1` and run `scripts/test.ps1`.
4. Reload an unpacked extension after extension changes. Check native-host identity when changing the manifest public key.
5. Describe behavior changes, validation and known limitations in your proposed change.

Never commit signing keys, access tokens, browser profiles, real download histories, SDK/runtime binaries or build output. Temporary tests should use local HTTP fixtures and separate app-data/download directories. Do not delete user files to test deletion behavior.

للتعديل: ابدأ بدليل البناء، وعدّل الملفات المناسبة ثم أعد البناء والاختبارات. أعد تحميل الإضافة بعد تغيير ملفاتها، وحافظ على توافق معرّفها مع موصل البرنامج. راجع الترخيص قبل إعادة توزيع نسخة معدّلة، ولا ترفع المفاتيح الخاصة أو بيانات المتصفح أو سجل التنزيلات.
