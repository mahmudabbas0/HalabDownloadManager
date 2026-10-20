[CmdletBinding()]
param([string]$Python='python',[string]$Node='node',[switch]$IncludeVideoBridge)
$ErrorActionPreference='Stop'
$repo=Split-Path -Parent $PSScriptRoot
$env:HALAB_TEST_EXE=Join-Path $repo 'build\package\App\HalabDownloadManager.exe'
$env:HALAB_TEST_APP=Split-Path -Parent $env:HALAB_TEST_EXE
$env:QT_QPA_PLATFORM='offscreen'
$env:PYTHONIOENCODING='utf-8'
if(!(Test-Path -LiteralPath $env:HALAB_TEST_EXE)){throw 'Build and deploy the application with scripts/build.ps1 first.'}
foreach($flag in '--delete-check','--lifecycle-check','--ui-check','--language-check'){
 $process=Start-Process -FilePath $env:HALAB_TEST_EXE -ArgumentList $flag -Wait -PassThru -WindowStyle Hidden
 if($process.ExitCode){throw "Application check failed: $flag ($($process.ExitCode))"}
}
foreach($test in 'integration_test.py','resume_test.py','naming_test.py'){
 & $Python (Join-Path $repo "tests\$test")
 if($LASTEXITCODE){throw "Test failed: $test"}
}
& $Node --test (Join-Path $repo 'tests\extension_test.mjs')
if($LASTEXITCODE){throw 'Browser extension unit tests failed.'}
if($IncludeVideoBridge){
 & $Python (Join-Path $repo 'tests\bridge_test.py')
 if($LASTEXITCODE){throw 'Optional video/native bridge test failed.'}
}
Write-Host 'All requested checks passed.'
