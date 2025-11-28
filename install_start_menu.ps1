# Create XENO Start Menu Entry
# Run with: powershell -ExecutionPolicy Bypass -File install_start_menu.ps1

Write-Host ""
Write-Host "Creating XENO Start Menu entry..." -ForegroundColor Cyan

$PythonExe = (Get-Command python).Source
$JarvisPath = Join-Path $PSScriptRoot "src\jarvis.py"
$IconPath = Join-Path $PSScriptRoot "assets\XENO.ico"
$WorkingDir = $PSScriptRoot

# Create XENO folder in Start Menu
$StartMenuPath = [Environment]::GetFolderPath("StartMenu")
$ProgramsPath = Join-Path $StartMenuPath "Programs"
$XENOFolder = Join-Path $ProgramsPath "XENO"

if (!(Test-Path $XENOFolder)) {
    New-Item -ItemType Directory -Path $XENOFolder -Force | Out-Null
    Write-Host "[OK] Created folder: $XENOFolder" -ForegroundColor Green
}

# Create main XENO shortcut
$MainShortcut = Join-Path $XENOFolder "XENO.lnk"
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($MainShortcut)
$Shortcut.TargetPath = $PythonExe
$Shortcut.Arguments = "`"$JarvisPath`""
$Shortcut.WorkingDirectory = $WorkingDir
$Shortcut.Description = "XENO - Personal AI Assistant"
$Shortcut.IconLocation = $IconPath
$Shortcut.Save()
Write-Host "[OK] Created: XENO.lnk" -ForegroundColor Green

# Create Settings shortcut
$SettingsShortcut = Join-Path $XENOFolder "XENO Settings.lnk"
$Shortcut2 = $WScriptShell.CreateShortcut($SettingsShortcut)
$Shortcut2.TargetPath = $PythonExe
$Shortcut2.Arguments = "`"$JarvisPath`" --setup"
$Shortcut2.WorkingDirectory = $WorkingDir
$Shortcut2.Description = "XENO Setup Wizard"
$Shortcut2.IconLocation = $IconPath
$Shortcut2.Save()
Write-Host "[OK] Created: XENO Settings.lnk" -ForegroundColor Green

# Create Documentation shortcut
$DocsPath = Join-Path $PSScriptRoot "SETUP_GUIDE.md"
$DocsShortcut = Join-Path $XENOFolder "Documentation.lnk"
$Shortcut3 = $WScriptShell.CreateShortcut($DocsShortcut)
$Shortcut3.TargetPath = $DocsPath
$Shortcut3.WorkingDirectory = $PSScriptRoot
$Shortcut3.Description = "XENO Documentation"
$Shortcut3.Save()
Write-Host "[OK] Created: Documentation.lnk" -ForegroundColor Green

# Create Uninstall shortcut
$UninstallScript = Join-Path $PSScriptRoot "uninstall.ps1"
$UninstallShortcut = Join-Path $XENOFolder "Uninstall XENO.lnk"
$Shortcut4 = $WScriptShell.CreateShortcut($UninstallShortcut)
$Shortcut4.TargetPath = "powershell.exe"
$Shortcut4.Arguments = "-ExecutionPolicy Bypass -File `"$UninstallScript`""
$Shortcut4.WorkingDirectory = $PSScriptRoot
$Shortcut4.Description = "Uninstall XENO"
$Shortcut4.Save()
Write-Host "[OK] Created: Uninstall XENO.lnk" -ForegroundColor Green

Write-Host ""
Write-Host "[SUCCESS] XENO Start Menu folder created!" -ForegroundColor Green
Write-Host ""
Write-Host "You can now find XENO in:" -ForegroundColor Cyan
Write-Host "  Start Menu -> Programs -> XENO" -ForegroundColor White
Write-Host ""
Write-Host "Shortcuts created:" -ForegroundColor Yellow
Write-Host "  - XENO (main application)" -ForegroundColor White
Write-Host "  - XENO Settings" -ForegroundColor White
Write-Host "  - Documentation" -ForegroundColor White
Write-Host "  - Uninstall XENO" -ForegroundColor White
Write-Host ""
