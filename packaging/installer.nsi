; ================================================================
; Jarvis V2 - NSIS Installer Script
; ================================================================
; Alternative to Inno Setup for building Install.exe
;
; Build with: makensis packaging\installer.nsi
;
; Output: dist\installer\JarvisV2-Setup.exe
; ================================================================

!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"
!include "WinVer.nsh"

; ----- Configuration -----
Name "Jarvis V2"
OutFile "..\dist\installer\JarvisV2-Setup.exe"
InstallDir "$PROGRAMFILES\JarvisV2"
InstallDirRegKey HKLM "Software\JarvisV2" "InstallDir"
RequestExecutionLevel admin
SetCompressor /SOLID lzma
Unicode True

; ----- Version Info -----
VIProductVersion "2.0.0.0"
VIAddVersionKey "ProductName" "Jarvis V2"
VIAddVersionKey "CompanyName" "jonathansteve-cell"
VIAddVersionKey "FileDescription" "All-in-One Desktop AI Assistant - Solar Core HUD"
VIAddVersionKey "FileVersion" "2.0.0"
VIAddVersionKey "ProductVersion" "2.0.0"
VIAddVersionKey "LegalCopyright" "Copyright 2026 jonathansteve-cell"

; ----- MUI Configuration -----
!define MUI_ABORTWARNING
!define MUI_ICON "app.ico"
!define MUI_UNICON "app.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "app.bmp"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "app.bmp"
!define MUI_HEADERIMAGE_RIGHT

; Welcome page text
!define MUI_WELCOMEPAGE_TITLE "Welcome to Jarvis V2 Setup"
!define MUI_WELCOMEPAGE_TEXT "This wizard will guide you through the installation of Jarvis V2.$\r$\n$\r$\nJarvis V2 is an all-in-one desktop AI assistant with voice control, a cinematic HUD, and 19 built-in modules.$\r$\n$\r$\nClick Next to continue."

; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\JarvisV2.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch Jarvis V2"
!define MUI_FINISHPAGE_LINK "Visit project on GitHub"
!define MUI_FINISHPAGE_LINK_LOCATION "https://github.com/jonathansteve-cell/JarvisV2"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\README.md"
!define MUI_FINISHPAGE_SHOWREADME_TEXT "View README"

; ----- Pages -----
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; ----- Languages -----
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "German"
!insertmacro MUI_LANGUAGE "French"
!insertmacro MUI_LANGUAGE "Spanish"
!insertmacro MUI_LANGUAGE "Japanese"
!insertmacro MUI_LANGUAGE "SimpChinese"

; ----- Installer Sections -----

Section "Jarvis V2 Core (required)" SecMain
    SectionIn RO
    
    ; Check Windows version
    ${IfNot} ${AtLeastWin10}
        MessageBox MB_OK "Jarvis V2 requires Windows 10 or later."
        Abort
    ${EndIf}
    
    SetOutPath "$INSTDIR"
    
    ; Install all files from PyInstaller output
    File /r "..\dist\JarvisV2\*.*"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; Registry entries for Add/Remove Programs
    WriteRegStr HKLM "Software\JarvisV2" "InstallDir" "$INSTDIR"
    WriteRegStr HKLM "Software\JarvisV2" "Version" "2.0.0"
    
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\JarvisV2" \
        "DisplayName" "Jarvis V2"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\JarvisV2" \
        "UninstallString" "$\"$INSTDIR\Uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\JarvisV2" \
        "QuietUninstallString" "$\"$INSTDIR\Uninstall.exe$\" /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\JarvisV2" \
        "DisplayIcon" "$\"$INSTDIR\JarvisV2.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\JarvisV2" \
        "Publisher" "jonathansteve-cell"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\JarvisV2" \
        "DisplayVersion" "2.0.0"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\JarvisV2" \
        "URLInfoAbout" "https://github.com/jonathansteve-cell/JarvisV2"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\JarvisV2" \
        "URLUpdateInfo" "https://github.com/jonathansteve-cell/JarvisV2/releases"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\JarvisV2" \
        "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\JarvisV2" \
        "NoRepair" 1
    
    ; Get installed size
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\JarvisV2" \
        "EstimatedSize" "$0"
    
    ; Create runtime directories
    CreateDirectory "$INSTDIR\data"
    CreateDirectory "$INSTDIR\logs"
    CreateDirectory "$INSTDIR\screenshots"
    CreateDirectory "$INSTDIR\documents"
    
    ; Copy config if not exists
    IfFileExists "$INSTDIR\.env" no_env
        CopyFiles "$INSTDIR\.env.example" "$INSTDIR\.env"
    no_env:
SectionEnd

Section "Desktop Shortcut" SecDesktop
    CreateShortCut "$DESKTOP\Jarvis V2.lnk" "$INSTDIR\JarvisV2.exe" "" "$INSTDIR\JarvisV2.exe" 0 SW_SHOWNORMAL "" "Launch Jarvis V2 - All-in-One Desktop AI Assistant with Solar Core HUD"
SectionEnd

Section "Start Menu Shortcuts" SecStartMenu
    CreateDirectory "$SMPROGRAMS\Jarvis V2"
    CreateShortCut "$SMPROGRAMS\Jarvis V2\Jarvis V2.lnk" "$INSTDIR\JarvisV2.exe" "" "$INSTDIR\JarvisV2.exe" 0 SW_SHOWNORMAL "" "Launch Jarvis V2"
    CreateShortCut "$SMPROGRAMS\Jarvis V2\Jarvis V2 (Voice Mode).lnk" "$INSTDIR\JarvisV2.exe" "--voice-only" "$INSTDIR\JarvisV2.exe" 0 SW_SHOWNORMAL "" "Launch Jarvis V2 in Voice Mode"
    CreateShortCut "$SMPROGRAMS\Jarvis V2\Jarvis V2 (Web Dashboard).lnk" "$INSTDIR\JarvisV2.exe" "--web" "$INSTDIR\JarvisV2.exe" 0 SW_SHOWNORMAL "" "Launch Jarvis V2 Web Dashboard"
    CreateShortCut "$SMPROGRAMS\Jarvis V2\Jarvis V2 (System Check).lnk" "$INSTDIR\JarvisV2.exe" "--check" "$INSTDIR\JarvisV2.exe" 0 SW_SHOWNORMAL "" "Run Jarvis V2 System Check"
    CreateShortCut "$SMPROGRAMS\Jarvis V2\Uninstall.lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\Uninstall.exe" 0
SectionEnd

Section "Quick Launch Shortcut" SecQuickLaunch
    CreateShortCut "$QUICKLAUNCH\Jarvis V2.lnk" "$INSTDIR\JarvisV2.exe" "" "$INSTDIR\JarvisV2.exe" 0 SW_SHOWNORMAL "" "Launch Jarvis V2"
SectionEnd

Section "Start with Windows (Voice Mode)" SecAutoStart
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "JarvisV2" \
        "$\"$INSTDIR\JarvisV2.exe$\" --voice-only"
SectionEnd

Section "Add to PATH" SecPath
    ; Read current PATH
    ReadRegStr $0 HKCU "Environment" "Path"
    ; Check if already in PATH
    ${StrContains} $1 $0 "$INSTDIR"
    StrCmp $1 "" add_path
        Goto done_path
    add_path:
        ; Append to PATH
        WriteRegExpandStr HKCU "Environment" "Path" "$0;$INSTDIR"
        ; Notify the system
        SendMessage ${HWND_BROADCAST} ${WM_WININICHANGING} 0 "STR:Environment" /TIMEOUT=5000
    done_path:
SectionEnd

; ----- Section Descriptions -----
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} "Install Jarvis V2 core files. This is required."
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} "Create a shortcut on the Desktop for quick access."
    !insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenu} "Create Start Menu shortcuts for Jarvis V2 and its modes."
    !insertmacro MUI_DESCRIPTION_TEXT ${SecQuickLaunch} "Create a Quick Launch shortcut for easy access."
    !insertmacro MUI_DESCRIPTION_TEXT ${SecAutoStart} "Launch Jarvis V2 in voice mode when Windows starts."
    !insertmacro MUI_DESCRIPTION_TEXT ${SecPath} "Add Jarvis V2 to the system PATH for command-line usage."
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; ----- Uninstaller Section -----
Section "Uninstall"
    ; Ask about user data
    MessageBox MB_YESNO "Do you want to remove user data (logs, screenshots, documents)?" IDYES remove_data IDNO keep_data
    remove_data:
        RMDir /r "$INSTDIR\data"
        RMDir /r "$INSTDIR\logs"
        RMDir /r "$INSTDIR\screenshots"
        RMDir /r "$INSTDIR\documents"
    keep_data:
    
    ; Remove installed files
    RMDir /r "$INSTDIR"
    
    ; Remove shortcuts
    Delete "$DESKTOP\Jarvis V2.lnk"
    Delete "$QUICKLAUNCH\Jarvis V2.lnk"
    RMDir /r "$SMPROGRAMS\Jarvis V2"
    
    ; Remove registry entries
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\JarvisV2"
    DeleteRegKey HKLM "Software\JarvisV2"
    DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "JarvisV2"
    
    ; Remove from PATH
    ReadRegStr $0 HKCU "Environment" "Path"
    ${StrRep} $0 $0 ";$INSTDIR" ""
    WriteRegExpandStr HKCU "Environment" "Path" "$0"
    SendMessage ${HWND_BROADCAST} ${WM_WININICHANGING} 0 "STR:Environment" /TIMEOUT=5000
    
    ; Notify user
    MessageBox MB_OK "Jarvis V2 has been uninstalled."
SectionEnd

; ----- Functions -----
Function .onInit
    ; Check if already installed
    ReadRegStr $0 HKLM "Software\JarvisV2" "InstallDir"
    StrCmp $0 "" not_installed
        MessageBox MB_YESCANCEL "Jarvis V2 is already installed. Do you want to reinstall?" IDYES continue_install IDCANCEL abort_install
    continue_install:
        Goto not_installed
    abort_install:
        Abort
    not_installed:
FunctionEnd
