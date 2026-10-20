[CmdletBinding()]
param(
 [string]$QtRoot = 'C:\Qt\6.10.1\mingw_64',
 [string]$MingwBin = 'C:\Qt\Tools\mingw1310_64\bin',
 [string]$CMake = 'C:\Qt\Tools\CMake_64\bin\cmake.exe',
 [string]$NinjaBin = 'C:\Qt\Tools\Ninja',
 [string]$NodeExe = '',
 [string]$Python = 'python',
 [string]$BrowserCrx = '',
 [string]$ExtensionKey = '',
 [string]$InnoCompiler = 'C:\Program Files (x86)\Inno Setup 6\ISCC.exe',
 [int]$Jobs = 4,
 [switch]$CreateInstaller
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$build = Join-Path $repo 'build'
$payload = Join-Path $build 'package\App'
$dist = Join-Path $repo 'dist'
if (!(Test-Path -LiteralPath (Join-Path $QtRoot 'bin\windeployqt.exe'))) { throw 'QtRoot must point to a Qt 6 MinGW SDK.' }
if (!(Test-Path -LiteralPath (Join-Path $MingwBin 'g++.exe'))) { throw 'MingwBin must point to the matching MinGW compiler bin directory.' }
if (!(Test-Path -LiteralPath $CMake)) { $CMake = (Get-Command cmake -ErrorAction Stop).Source }
if (!$NodeExe) { $NodeExe = (Get-Command node -ErrorAction Stop).Source }
if (!(Test-Path -LiteralPath $NodeExe)) { throw 'Pass -NodeExe with the path to node.exe.' }
$env:PATH = "$MingwBin;$NinjaBin;$(Join-Path $QtRoot 'bin');$env:PATH"
& $CMake -S $repo -B $build -G Ninja "-DCMAKE_PREFIX_PATH=$QtRoot" -DCMAKE_BUILD_TYPE=Release
if ($LASTEXITCODE) { throw 'CMake configuration failed.' }
& $CMake --build $build --parallel $Jobs
if ($LASTEXITCODE) { throw 'C++ build failed.' }
New-Item -ItemType Directory -Force -Path $payload,$dist,(Join-Path $payload 'tools'),(Join-Path $payload 'Browser') | Out-Null
Copy-Item -LiteralPath (Join-Path $build 'bin\HalabDownloadManager.exe'),(Join-Path $build 'bin\HalabNativeHost.exe') -Destination $payload -Force
& (Join-Path $QtRoot 'bin\windeployqt.exe') --release --compiler-runtime --dir $payload (Join-Path $payload 'HalabDownloadManager.exe')
if ($LASTEXITCODE) { throw 'Qt deployment failed.' }
foreach ($locale in 'ar','tr') {
 $catalog = Join-Path $QtRoot ("translations\qtbase_$locale.qm")
 if (Test-Path -LiteralPath $catalog) { Copy-Item -LiteralPath $catalog -Destination (Join-Path $payload 'translations') -Force }
}
$offscreen = Join-Path $QtRoot 'plugins\platforms\qoffscreen.dll'
if (Test-Path -LiteralPath $offscreen) { Copy-Item -LiteralPath $offscreen -Destination (Join-Path $payload 'platforms') -Force }
Copy-Item -LiteralPath (Join-Path $repo 'installer\com.mahmudabbas.halab.json') -Destination $payload -Force
Copy-Item -LiteralPath (Join-Path $repo 'third-party\licenses') -Destination $payload -Recurse -Force
Copy-Item -LiteralPath $NodeExe -Destination (Join-Path $payload 'tools\node.exe') -Force
Copy-Item -LiteralPath (Join-Path $repo 'third-party\node\LICENSE.txt') -Destination (Join-Path $payload 'tools\Node-LICENSE.txt') -Force
$packageArgs = @((Join-Path $PSScriptRoot 'package-extension.py'),'--output-dir',$dist)
if ($ExtensionKey) { $packageArgs += @('--key',$ExtensionKey) }
if ($BrowserCrx) { $packageArgs += @('--crx',$BrowserCrx) }
& $Python @packageArgs
if ($LASTEXITCODE) { throw 'Browser extension packaging failed.' }
$version = (Get-Content -LiteralPath (Join-Path $repo 'VERSION') -Raw).Trim()
$signedCrx = Join-Path $dist "HalabDownloadManager-$version-BrowserExtension.crx"
if (Test-Path -LiteralPath $signedCrx) { Copy-Item -LiteralPath $signedCrx -Destination (Join-Path $payload 'Browser\Halab Integration.crx') -Force }
if ($CreateInstaller) {
 if (!(Test-Path -LiteralPath $signedCrx)) { throw 'Installer needs a signed CRX. Pass -BrowserCrx from the release, or -ExtensionKey pointing to your private signing key outside this repository.' }
 if (!(Test-Path -LiteralPath $InnoCompiler)) { throw 'Pass -InnoCompiler with the Inno Setup 6 ISCC.exe path.' }
 & $InnoCompiler /Q (Join-Path $repo 'installer\Setup.iss')
 if ($LASTEXITCODE) { throw 'Installer compilation failed.' }
}
$files = Get-ChildItem -LiteralPath $dist -File | Where-Object { $_.Extension -in '.exe','.crx','.zip' } | Sort-Object Name
$lines = $files | ForEach-Object { '{0}  {1}' -f (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant(),$_.Name }
[IO.File]::WriteAllLines((Join-Path $dist 'SHA256SUMS.txt'),[string[]]$lines,(New-Object Text.UTF8Encoding $false))
Write-Host "Application: $payload"
Write-Host "Release assets: $dist"
