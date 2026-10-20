# Third-party notices

Original Halab application code, browser connector, artwork and installer: Copyright © 2026 Mahmud Abbas. This attribution does not transfer ownership of any dependency.

| Component | Distribution and notices |
| --- | --- |
| Qt 6.10.1 | Dynamically linked Core/Gui/Widgets/Network/Svg and plugins; license texts in `third-party/licenses/`. The build/install package copies them into its `licenses/` directory. Qt source: https://download.qt.io/archive/qt/6.10/6.10.1/single/ ; licensing: https://doc.qt.io/qt-6.10/licensing.html |
| MinGW GCC runtime / winpthreads | Runtime license notices included under `third-party/licenses/`. |
| Node.js 24.18.0 | Bundled by the build script; full upstream license in `third-party/node/LICENSE.txt`, copied beside the installed runtime. Source: https://nodejs.org/dist/v24.18.0/ and https://github.com/nodejs/node/tree/v24.18.0 |
| yt-dlp | Optional upstream executable downloaded by Inno Setup, not committed to Git or embedded in the base installer. The source project is Unlicense; official executable bundles contain additional GPLv3+ components. See https://github.com/yt-dlp/yt-dlp#licensing and the upstream release's notices/source. |
| FFmpeg | Optional BtbN Windows LGPL shared-build archive downloaded by the installer with its included documentation/licenses. Upstream source/build information: https://ffmpeg.org/download.html and https://github.com/BtbN/FFmpeg-Builds |
| Inno Setup | Installer compiler required for development; consult its distribution license. No compiler installation is redistributed in this source repository. https://jrsoftware.org/isinfo.php |

Compatible modified Qt runtime libraries may be used for relinking/replacement, subject to their own licenses. The original Halab license does not limit rights provided by third-party licenses, including reverse engineering needed to debug modifications to LGPL-covered libraries. Corresponding source/build instructions for Halab are included in this repository.

If you upgrade a dependency or distribute additional binaries, update the notices and comply with that dependency's license. This project has no affiliation with IDM, Google, Microsoft, YouTube, Qt or the upstream video-tool authors.
