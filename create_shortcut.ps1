# PowerShell script to create XENO desktop shortcut
# Run with: powershell -ExecutionPolicy Bypass -File create_shortcut.ps1

$PythonExe = (Get-Command python).Source
$JarvisPath = Join-Path $PSScriptRoot "src\jarvis.py"
$IconPath = Join-Path $PSScriptRoot "assets\xeno.ico"
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "XENO.lnk"
$WorkingDir = $PSScriptRoot

# Create shortcut
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $PythonExe
$Shortcut.Arguments = "`"$JarvisPath`""
$Shortcut.WorkingDirectory = $WorkingDir
$Shortcut.Description = "XENO - Personal AI Assistant"
$Shortcut.IconLocation = $IconPath
$Shortcut.Save()

Write-Host "[OK] Desktop shortcut created successfully!" -ForegroundColor Green
Write-Host "  Location: $ShortcutPath" -ForegroundColor Cyan
Write-Host "  Icon: $IconPath" -ForegroundColor Cyan

# Remove old batch file if exists
$BatchPath = Join-Path $DesktopPath "XENO.bat"
if (Test-Path $BatchPath) {
    Remove-Item $BatchPath
    Write-Host "  Removed old batch file" -ForegroundColor Yellow
}
