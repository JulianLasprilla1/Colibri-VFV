; ---------------------------------------------------------------------------
; Inno Setup Script for Validador de Datos JD
; ---------------------------------------------------------------------------

[Setup]
AppName=Colibri-VFV
AppVersion=1.1.0
DefaultDirName={pf}\Colibri-VFV
DefaultGroupName=Colibri-VFV
OutputBaseFilename=Colibri-VFV_Instalador
Compression=lzma
SolidCompression=yes
SetupIconFile="resources\colibri.ico"

[Files]
; Copiar el ejecutable empaquetado
Source: "dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion
; Copiar la carpeta de códigos
Source: "resources\codigos_municipios\*"; DestDir: "{app}\resources\codigos_municipios"; Flags: recursesubdirs createallsubdirs
; Copiar el archivo de usuarios
Source: "resources\users\users.xlsx"; DestDir: "{app}\resources\users"; Flags: ignoreversion
; (Opcional) Copiar el ícono si es necesario para otros fines
Source: "resources\colibri.ico"; DestDir: "{app}\resources"; Flags: ignoreversion

[Icons]
; Acceso directo en el menú de inicio usando el ícono incrustado en el ejecutable
Name: "{group}\Colibri-VFV"; Filename: "{app}\main.exe"; IconFilename: "{app}\main.exe"
; Acceso directo en el escritorio (opcional)
Name: "{userdesktop}\Colibri-VFV"; Filename: "{app}\main.exe"; IconFilename: "{app}\main.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear un acceso directo en el escritorio"; Flags: unchecked

[Run]
Filename: "{app}\main.exe"; Description: "Ejecutar Colibri-VFV"; Flags: nowait postinstall skipifsilent
