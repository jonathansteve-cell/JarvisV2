; ================================================================
; Jarvis V2 - Professional Windows Installer (Inno Setup 6)
; ================================================================
; Build with:  packaging\BuildInstaller.bat
; Or manually: "C:\Program Files\Inno Setup 6\ISCC.exe" packaging\installer.iss
;
; Output: dist\installer\JarvisV2-Setup.exe
; ================================================================

#define MyAppName "Jarvis V2"
#define MyAppNameShort "JarvisV2"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "jonathansteve-cell"
#define MyAppURL "https://github.com/jonathansteve-cell/JarvisV2"
#define MyAppExeName "JarvisV2.exe"
#define MyAppDescription "All-in-One Desktop AI Assistant - Solar Core HUD"

[Setup]
; NOTE: The AppId uniquely identifies this application.
; Do not use the same AppId in installers for other applications.
AppId={{8F3B2A9E-4C71-4C6B-9B2E-2D1A5E0F0C21}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
AppCopyright=Copyright (C) 2026 {#MyAppPublisher}
VersionInfoVersion={#MyAppVersion}.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppDescription}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

; Installation directories
DefaultDirName={autopf}\{#MyAppNameShort}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE

; Output settings
OutputDir=..\dist\installer
OutputBaseFilename=JarvisV2-Setup
SetupIconFile=app.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

; Compression
Compression=lzma2/ultra64
SolidCompression=yes
LZMANumBlockThreads=4

; Appearance
WizardStyle=modern
WizardSizePercent=110
WizardImageFile=app.bmp
WizardSmallImageFile=app.ico

; Architecture
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; Misc
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
CloseApplications=yes
RestartApplications=no
SetupLogging=yes
MinVersion=10.0
ShowLanguageDialog=no

; ================================================================
; Languages
; ================================================================
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "portuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"
Name: "chinese"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

; ================================================================
; Files to install
; ================================================================
[Files]
; Main application files (PyInstaller output)
Source: "..\dist\{#MyAppNameShort}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; ================================================================
; Tasks (optional components)
; ================================================================
[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: checkedonce
Name: "startmenu"; Description: "Create &Start Menu shortcuts"; GroupDescription: "Additional shortcuts:"; Flags: checkedonce
Name: "quicklaunchicon"; Description: "Create a &Quick Launch shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked
Name: "autostart"; Description: "Start Jarvis V2 with &Windows"; GroupDescription: "Startup:"; Flags: unchecked
Name: "associatefiles"; Description: "Associate .jarvis files with &Jarvis V2"; GroupDescription: "File associations:"; Flags: unchecked

; ================================================================
; Icons / Shortcuts
; ================================================================
[Icons]
; Start Menu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "Launch {#MyAppName} - All-in-One Desktop AI Assistant"; IconFilename: "{app}\{#MyAppExeName}"; IconIndex: 0; Tasks: startmenu
Name: "{group}\{#MyAppName} Voice Mode"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--voice-only"; Comment: "Launch {#MyAppName} in voice-only mode"; Tasks: startmenu
Name: "{group}\{#MyAppName} Web Dashboard"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--web"; Comment: "Launch {#MyAppName} web dashboard at localhost:8765"; Tasks: startmenu
Name: "{group}\{#MyAppName} System Check"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--check"; Comment: "Run system check and diagnostics"; Tasks: startmenu
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"; Comment: "Uninstall {#MyAppName}"; Tasks: startmenu

; Desktop - PRIMARY SHORTCUT
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "Launch {#MyAppName} - All-in-One Desktop AI Assistant with Solar Core HUD"; IconFilename: "{app}\{#MyAppExeName}"; IconIndex: 0; WorkingDir: "{app}"; Tasks: desktopicon

; Quick Launch
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "Launch {#MyAppName}"; Tasks: quicklaunchicon

; Startup (auto-start with Windows)
Name: "{userstartup}\{#MyAppNameShort}"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--voice-only"; Comment: "Start Jarvis V2 with Windows (Voice Mode)"; Tasks: autostart

; ================================================================
; Registry entries
; ================================================================
[Registry]
; File association
Root: HKA; Subkey: "Software\Classes\.jarvis"; ValueType: string; ValueName: ""; ValueData: "JarvisV2File"; Flags: uninsdeletevalue; Tasks: associatefiles
Root: HKA; Subkey: "Software\Classes\JarvisV2File"; ValueType: string; ValueName: ""; ValueData: "Jarvis V2 Configuration"; Flags: uninsdeletekey; Tasks: associatefiles
Root: HKA; Subkey: "Software\Classes\JarvisV2File\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"; Tasks: associatefiles
Root: HKA; Subkey: "Software\Classes\JarvisV2File\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: associatefiles

; Add to PATH (optional, for CLI usage)
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}"; Check: NeedsAddPath('{app}')

; ================================================================
; INI configuration
; ================================================================
[INI]
Filename: "{app}\install_info.ini"; Section: "InstallInfo"; Key: "InstallDate"; String: "{%DATE|yyyy-MM-dd}"
Filename: "{app}\install_info.ini"; Section: "InstallInfo"; Key: "InstallVersion"; String: "{#MyAppVersion}"
Filename: "{app}\install_info.ini"; Section: "InstallInfo"; Key: "InstallPath"; String: "{app}"

; ================================================================
; Run after install
; ================================================================
[Run]
; Launch the app
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName} now"; Flags: nowait postinstall skipifsilent shellexec
; Open the README
Filename: "{app}\README.md"; Description: "View README"; Flags: nowait postinstall skipifsilent shellexec unchecked

; ================================================================
; Uninstall - clean up runtime data (ask user)
; ================================================================
[UninstallDelete]
Type: filesandordirs; Name: "{app}\data"
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\screenshots"
Type: filesandordirs; Name: "{app}\documents"
Type: files; Name: "{app}\install_info.ini"
Type: files; Name: "{app}\.env"

; ================================================================
; Code - custom Pascal Script functions
; ================================================================
[Code]
var
  DataDirPage: TInputDirWizardPage;

function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', OrigPath) then
  begin
    Result := True;
    exit;
  end;
  Result := Pos(';' + Param + ';', ';' + OrigPath + ';') = 0;
end;

procedure InitializeWizard;
begin
  { Create a custom page to let users choose where to store data }
  DataDirPage := CreateInputDirPage(wpSelectDir,
    'Data Storage Location', 'Where should Jarvis store its data?',
    'Jarvis will store memory, logs, screenshots, and documents in this folder.' + #13#10 + #13#10 +
    'Select a folder, or click Next to use the default location.',
    False, '');
  DataDirPage.Add('Data folder:');
  DataDirPage.Values[0] := ExpandConstant('{app}\data');
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = DataDirPage.ID then
  begin
    if not DirExists(DataDirPage.Values[0]) then
    begin
      if not CreateDir(DataDirPage.Values[0]) then
      begin
        MsgBox('Cannot create data folder: ' + DataDirPage.Values[0] + #13#10 +
               'Please choose a different location.', mbError, MB_OK);
        Result := False;
      end;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  DataDir: string;
begin
  if CurStep = ssPostInstall then
  begin
    { Create runtime directories }
    DataDir := DataDirPage.Values[0];
    CreateDir(DataDir);
    CreateDir(DataDir + '\logs');
    CreateDir(DataDir + '\screenshots');
    CreateDir(DataDir + '\documents');
    
    { Write data path to config if needed }
    SaveStringToFile(ExpandConstant('{app}\data_path.txt'), DataDir, False);
  end;
end;
