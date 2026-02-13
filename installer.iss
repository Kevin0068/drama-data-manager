[Setup]
AppName=剧名数据管理系统
AppVersion=1.1.0
DefaultDirName={autopf}\DramaDataManager
DefaultGroupName=剧名数据管理系统
OutputDir=installer_output
OutputBaseFilename=DramaDataManager_Setup
Compression=lzma
SolidCompression=yes
UninstallDisplayName=剧名数据管理系统
SetupIconFile=assets\app.ico

[Files]
Source: "dist\DramaDataManager.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\app.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\剧名数据管理系统"; Filename: "{app}\DramaDataManager.exe"; IconFilename: "{app}\app.ico"
Name: "{commondesktop}\剧名数据管理系统"; Filename: "{app}\DramaDataManager.exe"; IconFilename: "{app}\app.ico"

[Run]
Filename: "{app}\DramaDataManager.exe"; Description: "启动剧名数据管理系统"; Flags: nowait postinstall skipifsilent
