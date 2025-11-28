# XENO AI Agent + Job Hunter Installation Script
# Run this to setup everything automatically

Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         XENO v2.0 - AI Agent Installation              ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  ❌ Python not found!" -ForegroundColor Red
    Write-Host "  Please install Python 3.10+ from: https://python.org" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host ""
Write-Host "[2/5] Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Some packages failed. You may need to install manually." -ForegroundColor Yellow
}

# Check .env file
Write-Host ""
Write-Host "[3/5] Checking .env configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  ✅ .env file found" -ForegroundColor Green
    
    # Check for Gemini API key
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "GEMINI_API_KEY=\S+") {
        Write-Host "  ✅ Gemini API key configured" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Gemini API key not configured (optional)" -ForegroundColor Yellow
        Write-Host "     Get one at: https://makersuite.google.com/app/apikey" -ForegroundColor Gray
    }
} else {
    Write-Host "  ❌ .env file not found!" -ForegroundColor Red
    Write-Host "  Creating .env from template..." -ForegroundColor Yellow
    
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "  ✅ .env created. Please configure your API keys." -ForegroundColor Green
    } else {
        Write-Host "  ❌ .env.example not found. Please create .env manually." -ForegroundColor Red
    }
}

# Check Ollama
Write-Host ""
Write-Host "[4/5] Checking Ollama (Local AI)..." -ForegroundColor Yellow
try {
    $ollamaCheck = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "  ✅ Ollama is running" -ForegroundColor Green
    
    # Check for models
    $models = (Invoke-WebRequest -Uri "http://localhost:11434/api/tags").Content | ConvertFrom-Json
    if ($models.models.Count -gt 0) {
        Write-Host "  ✅ Models installed:" -ForegroundColor Green
        foreach ($model in $models.models) {
            Write-Host "     - $($model.name)" -ForegroundColor Gray
        }
    } else {
        Write-Host "  ⚠️  No models installed" -ForegroundColor Yellow
        Write-Host "     Install a model: ollama pull llama3.1:8b" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ⚠️  Ollama not detected (optional)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  To use local AI (recommended for RTX 4050):" -ForegroundColor Cyan
    Write-Host "  1. Download: https://ollama.ai/download" -ForegroundColor Gray
    Write-Host "  2. Install Ollama" -ForegroundColor Gray
    Write-Host "  3. Run: ollama pull llama3.1:8b" -ForegroundColor Gray
}

# Create directories
Write-Host ""
Write-Host "[5/5] Creating data directories..." -ForegroundColor Yellow
$directories = @(
    "data/jobs",
    "data/jobs/applications",
    "data/temp"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✅ Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "  ✅ Exists: $dir" -ForegroundColor Green
    }
}

# Summary
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║              Installation Complete!                     ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "🎯 Next Steps:" -ForegroundColor Yellow
Write-Host ""

# Check AI status
$hasOllama = $false
$hasGemini = $false

try {
    $ollamaCheck = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 1 -ErrorAction Stop
    $hasOllama = $true
} catch { }

if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "GEMINI_API_KEY=\S+") {
        $hasGemini = $true
    }
}

if (-not $hasOllama -and -not $hasGemini) {
    Write-Host "⚠️  No AI provider configured!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Choose one:" -ForegroundColor Cyan
    Write-Host "  Option 1: Local AI (Ollama) - Recommended" -ForegroundColor White
    Write-Host "    - Download: https://ollama.ai/download" -ForegroundColor Gray
    Write-Host "    - Run: ollama pull llama3.1:8b" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Option 2: Cloud AI (Gemini)" -ForegroundColor White
    Write-Host "    - Get key: https://makersuite.google.com/app/apikey" -ForegroundColor Gray
    Write-Host "    - Add to .env: GEMINI_API_KEY=your_key" -ForegroundColor Gray
    Write-Host ""
} else {
    if ($hasOllama) {
        Write-Host "✅ Local AI (Ollama) ready!" -ForegroundColor Green
    }
    if ($hasGemini) {
        Write-Host "✅ Cloud AI (Gemini) ready!" -ForegroundColor Green
    }
    Write-Host ""
}

Write-Host "📚 Documentation:" -ForegroundColor Yellow
Write-Host "  - AI Setup Guide: AI_SETUP.md" -ForegroundColor Gray
Write-Host "  - Job Hunting Guide: JOB_HUNTING_GUIDE.md" -ForegroundColor Gray
Write-Host "  - What's New: WHATS_NEW_V2.md" -ForegroundColor Gray
Write-Host ""

Write-Host "🚀 Quick Start:" -ForegroundColor Yellow
Write-Host "  1. Test AI:         python demos\demo_ai_agent.py" -ForegroundColor Gray
Write-Host "  2. Test Job Hunter: python demos\demo_job_hunter.py" -ForegroundColor Gray
Write-Host "  3. Prepare resume:  Create my_resume.txt" -ForegroundColor Gray
Write-Host "  4. Start hunting:   Follow JOB_HUNTING_GUIDE.md" -ForegroundColor Gray
Write-Host ""

Write-Host "🎉 XENO AI Agent is ready to help you find your Data Science internship!" -ForegroundColor Cyan
Write-Host ""
