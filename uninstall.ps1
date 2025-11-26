# XENO Uninstaller
# Removes shortcuts and auto-start entries

Write-Host ""
Write-Host "================================" -ForegroundColor Red
Write-Host "  XENO Uninstaller" -ForegroundColor Red
Write-Host "================================" -ForegroundColor Red
Write-Host ""

$confirm = Read-Host "Are you sure you want to uninstall XENO? (Y/N)"
if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "Uninstall cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Removing XENO..." -ForegroundColor Yellow

# Remove desktop shortcut
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$DesktopShortcut = Join-Path $DesktopPath "XENO.lnk"
if (Test-Path $DesktopShortcut) {
    Remove-Item $DesktopShortcut -Force
    Write-Host "[OK] Removed desktop shortcut" -ForegroundColor Green
}

# Remove batch file if exists
$BatchFile = Join-Path $DesktopPath "XENO.bat"
if (Test-Path $BatchFile) {
    Remove-Item $BatchFile -Force
    Write-Host "[OK] Removed batch file" -ForegroundColor Green
}

# Remove Start Menu folder
$StartMenuPath = [Environment]::GetFolderPath("StartMenu")
$ProgramsPath = Join-Path $StartMenuPath "Programs"
$XENOFolder = Join-Path $ProgramsPath "XENO"
if (Test-Path $XENOFolder) {
    Remove-Item $XENOFolder -Recurse -Force
    Write-Host "[OK] Removed Start Menu folder" -ForegroundColor Green
}

# Remove auto-start entry
try {
    $RegPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
    Remove-ItemProperty -Path $RegPath -Name "XENO" -ErrorAction SilentlyContinue
    Write-Host "[OK] Removed auto-start entry" -ForegroundColor Green
} catch {
    Write-Host "[INFO] Auto-start entry not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "  Uninstall Complete" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "XENO shortcuts and auto-start have been removed." -ForegroundColor Green
Write-Host ""
Write-Host "Note: Your data and configuration are preserved at:" -ForegroundColor Yellow
Write-Host "  $env:USERPROFILE\.XENO\" -ForegroundColor White
Write-Host ""
Write-Host "To completely remove all data, delete that folder manually." -ForegroundColor Yellow
Write-Host "To remove the application files, delete:" -ForegroundColor Yellow
Write-Host "  $PSScriptRoot" -ForegroundColor White
Write-Host ""
