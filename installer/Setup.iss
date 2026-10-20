#define Product "Halab Download Manager"
[Setup]
AppId={{CC71B2F4-7D27-49E0-8914-7A2E4166D283}
AppName={#Product}
AppVersion=1.0.3
AppPublisher=Mahmud Abbas
AppCopyright=Copyright (c) 2026 Mahmud Abbas
DefaultDirName={commonpf32}\Halab Download Manager
PrivilegesRequired=admin
UsePreviousAppDir=no
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
DisableWelcomePage=no
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\HalabDownloadManager.exe
SetupIconFile=..\src\halab.ico
OutputDir=..\dist
OutputBaseFilename=HalabDownloadManager-1.0.3-Setup
Compression=lzma2
SolidCompression=yes
ArchiveExtraction=full
CloseApplications=yes
RestartApplications=no
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "arabic"; MessagesFile: "compiler:Languages\Arabic.isl"
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"
[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; Flags: unchecked
Name: "video"; Description: "Video download support (Internet connection required)"; Flags: checkedonce
[Files]
Source: "..\build\package\App\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{tmp}\yt-dlp.exe"; DestDir: "{app}\tools"; Flags: external ignoreversion; Tasks: video
Source: "{tmp}\video-support.zip"; DestDir: "{app}\tools\ffmpeg"; Flags: external extractarchive recursesubdirs ignoreversion; Tasks: video
[Icons]
Name: "{autoprograms}\{#Product}"; Filename: "{app}\HalabDownloadManager.exe"
Name: "{autodesktop}\{#Product}"; Filename: "{app}\HalabDownloadManager.exe"; Tasks: desktopicon
[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "HalabDownloadManager"; ValueData: """{app}\HalabDownloadManager.exe"" --background"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Google\Chrome\NativeMessagingHosts\com.mahmudabbas.halab"; ValueType: string; ValueData: "{app}\com.mahmudabbas.halab.json"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Microsoft\Edge\NativeMessagingHosts\com.mahmudabbas.halab"; ValueType: string; ValueData: "{app}\com.mahmudabbas.halab.json"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Chromium\NativeMessagingHosts\com.mahmudabbas.halab"; ValueType: string; ValueData: "{app}\com.mahmudabbas.halab.json"; Flags: uninsdeletekey
[Run]
Filename: "{app}\HalabDownloadManager.exe"; Description: "{cm:LaunchProgram,{#Product}}"; Flags: nowait postinstall skipifsilent
[Code]
var DownloadPage: TDownloadWizardPage;
procedure InitializeWizard;
begin
 DownloadPage := CreateDownloadPage(SetupMessage(msgWizardPreparing), SetupMessage(msgPreparingDesc), nil);
 DownloadPage.ShowBaseNameInsteadOfUrl := True;
end;
function NextButtonClick(CurPageID: Integer): Boolean;
begin
 Result := True;
 if (CurPageID = wpReady) and WizardIsTaskSelected('video') then begin
  DownloadPage.Clear;
  DownloadPage.Add('https://github.com/yt-dlp/yt-dlp/releases/download/2026.08.19/yt-dlp.exe', 'yt-dlp.exe', '66674953fe251b89f4d08c5f0e35e0728679bd67ab3d7d05c0562af101dd3e7a');
  DownloadPage.Add('https://github.com/BtbN/FFmpeg-Builds/releases/download/autobuild-2026-10-19-13-06/ffmpeg-N-127696-g8b3525e718-win64-lgpl-shared.zip', 'video-support.zip', 'bbc654bf04dfa6bad883c345a758cda6000b51150e9ebd09529bb36517fdeb33');
  DownloadPage.Show;
  try
   try DownloadPage.Download;
   except
    if not DownloadPage.AbortedByUser then SuppressibleMsgBox(GetExceptionMessage, mbError, MB_OK, IDOK);
    Result := False;
   end;
  finally DownloadPage.Hide; end;
 end;
end;
