# JARVIS Personal AI Assistant - Installation Script
# For Windows PowerShell

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   JARVIS Personal AI Assistant Installer" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
    
    # Extract version number
    $versionMatch = [regex]::Match($pythonVersion, "(\d+)\.(\d+)")
    $majorVersion = [int]$versionMatch.Groups[1].Value
    $minorVersion = [int]$versionMatch.Groups[2].Value
    
    if ($majorVersion -lt 3 -or ($majorVersion -eq 3 -and $minorVersion -lt 11)) {
        Write-Host "Error: Python 3.11 or higher required!" -ForegroundColor Red
        Write-Host "Please download from: https://www.python.org/downloads/" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "Error: Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.11+ from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

if (-not $?) {
    Write-Host "Error: Failed to create virtual environment!" -ForegroundColor Red
    exit 1
}

Write-Host "Virtual environment created successfully!" -ForegroundColor Green
Write-Host ""

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray

pip install --upgrade pip
pip install -r requirements.txt

if (-not $?) {
    Write-Host "Error: Failed to install dependencies!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "   Installation Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Get an API key from OpenAI or Google Gemini" -ForegroundColor White
Write-Host "   - OpenAI: https://platform.openai.com/api-keys" -ForegroundColor Gray
Write-Host "   - Gemini: https://makersuite.google.com/app/apikey" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Run JARVIS:" -ForegroundColor White
Write-Host "   python src\jarvis.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Complete the setup wizard" -ForegroundColor White
Write-Host ""
Write-Host "For more information, see QUICKSTART.md" -ForegroundColor Yellow
Write-Host ""

# Ask if user wants to start JARVIS now
$response = Read-Host "Would you like to start JARVIS now? (Y/N)"
if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host ""
    Write-Host "Starting JARVIS..." -ForegroundColor Cyan
    python src\jarvis.py
} else {
    Write-Host ""
    Write-Host "You can start JARVIS later by running: python src\jarvis.py" -ForegroundColor Yellow
}
