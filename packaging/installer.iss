; Jarvis V2 - Windows installer (Inno Setup 6, https://jrsoftware.org/isdl.php)
; 1) Run packaging\build_exe.bat first (creates dist\JarvisV2\JarvisV2.exe)
; 2) Open this file in Inno Setup -> Build -> Compile
; Output: dist\installer\JarvisV2-Setup.exe
#define MyAppName "Jarvis V2"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "jonathansteve-cell"
#define MyAppExeName "JarvisV2.exe"

[Setup]
AppId={{8F3B2A9E-4C71-4C6B-9B2E-2D1A5E0F0C21}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\JarvisV2
DefaultGroupName=Jarvis V2
DisableProgramGroupPage=yes
OutputDir=..\dist\installer
OutputBaseFilename=JarvisV2-Setup
Compression=lzma2
SolidCompression=yes
SetupIconFile=app.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
WizardStyle=modern
; The app is a 64-bit PyInstaller build of a contains-64-bit Python.
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "..\dist\JarvisV2\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: checkedonce

[Icons]
Name: "{group}\Jarvis V2"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Jarvis V2"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Jarvis V2 now"; Flags: nowait postinstall skipifsilent