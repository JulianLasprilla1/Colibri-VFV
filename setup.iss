; ---------------------------------------------------------------------------
; Inno Setup Script for Validador de Datos JD
; ---------------------------------------------------------------------------

[Setup]
AppName=Colibrí-VFV JD
AppVersion=1.0.0
; Directorio predeterminado de instalación: usa {pf} para Program Files
DefaultDirName={pf}\Colibrí-VFV_JD
; Grupo de menú de inicio
DefaultGroupName=Colibrí-VFV JD
; Nombre del archivo instalador de salida
OutputBaseFilename=Colibrí-VFV_JD_Instalador
Compression=lzma
SolidCompression=yes
; Ruta del icono que se usará para el instalador
SetupIconFile= "resources\colibri.ico"

[Files]
; Copiar el ejecutable empaquetado
Source: "dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion
; Copiar la carpeta de recursos (asegúrate de que la ruta corresponda a tu estructura)
Source: "resources\codigos_municipios\*"; DestDir: "{app}\resources\codigos_municipios"; Flags: recursesubdirs createallsubdirs

[Icons]
; Crear acceso directo en el menú de inicio
Name: "{group}\Colibrí-VFV JD"; Filename: "{app}\main.exe"
; Crear acceso directo en el escritorio (esta tarea se activa o desactiva según el usuario)
Name: "{userdesktop}\Colibrí-VFV JD"; Filename: "{app}\main.exe"; Tasks: desktopicon

[Tasks]
; Tarea opcional para crear un acceso directo en el escritorio (desactivada por defecto)
Name: "desktopicon"; Description: "Crear un acceso directo en el escritorio"; Flags: unchecked

[Run]
; Ejecutar la aplicación al finalizar la instalación (opcional)
Filename: "{app}\main.exe"; Description: "Ejecutar Colibrí-VFV JD"; Flags: nowait postinstall skipifsilent
