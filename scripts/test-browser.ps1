[CmdletBinding()]
param(
 [Parameter(Mandatory=$true)][string]$BrowserExe,
 [ValidateSet('Chrome','Edge')][string]$BrowserFamily='Chrome',
 [string]$Python='python',
 [string]$Node='node',
 [switch]$KeepArtifacts
)
$ErrorActionPreference='Stop'
$repo=Split-Path -Parent $PSScriptRoot
if(!(Test-Path -LiteralPath $BrowserExe)){throw 'Pass the path to an official Chrome for Testing browser executable.'}
$tempBase=[IO.Path]::GetFullPath([IO.Path]::GetTempPath())
$testRoot=Join-Path $tempBase ('halab-browser-e2e-'+[guid]::NewGuid().ToString('N'))
$env:HALAB_E2E_ROOT=$testRoot
$env:HALAB_E2E_HOST='com.mahmudabbas.halab.e2e'+[guid]::NewGuid().ToString('N').Substring(0,12)
$env:HALAB_E2E_BROWSER=[IO.Path]::GetFullPath($BrowserExe)
$env:PYTHONIOENCODING='utf-8'
$vendor=if($BrowserFamily -eq 'Edge'){'Microsoft\Edge'}else{'Google\Chrome'}
$key="HKCU:\Software\$vendor\NativeMessagingHosts\$env:HALAB_E2E_HOST"
$ownedKey=$false
try{
 & $Python (Join-Path $repo 'tests\prepare_browser_e2e.py')
 if($LASTEXITCODE){throw 'Browser test preparation failed.'}
 if(Test-Path -LiteralPath $key){throw 'Temporary test registry key unexpectedly exists.'}
 New-Item -Path $key -Force|Out-Null
 $ownedKey=$true
 Set-Item -LiteralPath $key -Value (Join-Path $testRoot 'native.json')
 & $Node (Join-Path $repo 'tests\browser_e2e.mjs')
 if($LASTEXITCODE){throw 'Real browser/native integration test failed.'}
}finally{
 if($ownedKey){Remove-Item -LiteralPath $key -Force -ErrorAction SilentlyContinue}
 if($KeepArtifacts){Write-Host "Test artifacts: $testRoot"}
 else{
  $targets=@($testRoot)
  $record=Join-Path $testRoot 'browser-profile-path.txt'
  if(Test-Path -LiteralPath $record){$targets+=((Get-Content -LiteralPath $record -Raw).Trim())}
  foreach($target in $targets){
   $full=[IO.Path]::GetFullPath($target)
   $name=[IO.Path]::GetFileName($full)
   if(!$full.StartsWith($tempBase,[StringComparison]::OrdinalIgnoreCase) -or (!$name.StartsWith('halab-browser-e2e-') -and !$name.StartsWith('halab-e2e-'))){throw 'Refusing cleanup outside the explicitly named temporary test directories.'}
   if(Test-Path -LiteralPath $full){Remove-Item -LiteralPath $full -Recurse -Force -ErrorAction SilentlyContinue}
  }
 }
}
