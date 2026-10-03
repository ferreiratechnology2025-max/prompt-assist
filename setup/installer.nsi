; Nex-Júris NSIS Installer
; Compile with: makensis installer.nsi

!define PRODUCT_NAME "Nex-Júris"
!define PRODUCT_VERSION "1.0.0"
!define PRODUCT_PUBLISHER "Nex-Júris"

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "..\dist\nexjuris-setup.exe"
InstallDir "$PROGRAMFILES64\${PRODUCT_NAME}"
RequestExecutionLevel admin

Section "Install"
    SetOutPath "$INSTDIR"

    File /r "..\dist\nexjuris-backend.exe"
    File /r "..\frontend\dist\*.*"

    CreateDirectory "$INSTDIR\storage"
    CreateDirectory "$INSTDIR\storage\database"
    CreateDirectory "$INSTDIR\storage\uploads"
    CreateDirectory "$INSTDIR\storage\pecas"
    CreateDirectory "$INSTDIR\storage\logs"

    CreateShortCut "$DESKTOP\${PRODUCT_NAME}.lnk" "$INSTDIR\nexjuris-backend.exe"
    CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk" "$INSTDIR\nexjuris-backend.exe"
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe"

    WriteUninstaller "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "DisplayName" "${PRODUCT_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "UninstallString" "$INSTDIR\uninstall.exe"
SectionEnd

Section "Uninstall"
    RMDir /r "$INSTDIR"
    Delete "$DESKTOP\${PRODUCT_NAME}.lnk"
    RMDir /r "$SMPROGRAMS\${PRODUCT_NAME}"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
SectionEnd
