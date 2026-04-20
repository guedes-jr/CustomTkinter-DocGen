[Setup]
AppName=DocGen Pro
AppVersion=1.0
DefaultDirName={autopf}\DocGen Pro
DefaultGroupName=DocGen Pro
UninstallDisplayIcon={app}\DocGen Pro.exe
Compression=lzma2
SolidCompression=yes
OutputDir=dist
OutputBaseFilename=Instalador_DocGen_Pro
SetupIconFile=assets\icon.ico

[Files]
; Aqui estamos dizendo para o Inno Setup copiar o .exe (que o PyInstaller gerou) para o computador do cliente
Source: "dist\DocGen Pro.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Atalho no Menu Iniciar
Name: "{group}\DocGen Pro"; Filename: "{app}\DocGen Pro.exe"
; Atalho na Area de Trabalho
Name: "{autodesktop}\DocGen Pro"; Filename: "{app}\DocGen Pro.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar um atalho na Area de Trabalho"; GroupDescription: "Atalhos adicionais:"
