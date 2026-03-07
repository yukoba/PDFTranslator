[Setup]
AppName=PDF Translator
AppVersion=1.1.0
DefaultDirName={autopf}\PDFTranslator
DefaultGroupName=PDF Translator
OutputDir=.\dist\installer
OutputBaseFilename=PDFTranslator_Setup
Compression=lzma
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\PDFTranslator\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\PDF Translator"; Filename: "{app}\PDFTranslator.exe"
Name: "{commondesktop}\PDF Translator"; Filename: "{app}\PDFTranslator.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\PDFTranslator.exe"; Description: "{cm:LaunchProgram,PDF Translator}"; Flags: nowait postinstall skipifsilent
