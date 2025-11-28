# XENO Startup Script
# Starts XENO detached from terminal so it can run in background

$XenoPath = "E:\Personal assistant"
$VenvPython = Join-Path $XenoPath ".venv\Scripts\python.exe"
$JarvisScript = Join-Path $XenoPath "src\jarvis.py"

Write-Host "[*] Starting XENO..." -ForegroundColor Cyan

# Check if files exist
if (-not (Test-Path $VenvPython)) {
    Write-Host "[ERROR] Python not found: $VenvPython" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $JarvisScript)) {
    Write-Host "[ERROR] Jarvis script not found: $JarvisScript" -ForegroundColor Red
    exit 1
}

# Start XENO in a new process, detached from this terminal
$process = Start-Process -FilePath $VenvPython `
              -ArgumentList $JarvisScript `
              -WorkingDirectory $XenoPath `
              -WindowStyle Hidden `
              -PassThru

if ($process) {
    Write-Host "[*] XENO process started (PID: $($process.Id))" -ForegroundColor Cyan
} else {
    Write-Host "[ERROR] Failed to start process" -ForegroundColor Red
    exit 1
}

Start-Sleep -Seconds 5

# Check if XENO is running
$xeno = Get-Process python -ErrorAction SilentlyContinue
if ($xeno) {
    Write-Host "[OK] XENO is running! (PID: $($xeno.Id))" -ForegroundColor Green
    Write-Host "[*] Check your system tray for the XENO icon" -ForegroundColor Yellow
    Write-Host "[*] Voice commands are active - say 'Hey XENO' to interact" -ForegroundColor Green
} else {
    Write-Host "[ERROR] XENO failed to start" -ForegroundColor Red
}
