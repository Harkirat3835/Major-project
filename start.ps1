# Fake News Detector - Complete Startup Script
# This script sets up and runs the entire project in one go

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontendDir = Join-Path $root 'frontend'
$venvPath = Join-Path $root '.venv'
$venvActivate = Join-Path $venvPath 'Scripts\Activate.ps1'

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "     Fake News Detector - Professional Edition" -ForegroundColor Cyan
Write-Host "               Complete Setup & Launch" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Setup Python Virtual Environment
Write-Host "[1/5] Setting up Python environment..." -ForegroundColor Yellow
if (-Not (Test-Path $venvPath)) {
    Write-Host "      Creating virtual environment..." -ForegroundColor Gray
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "      Virtual environment already exists." -ForegroundColor Green
}

# Activate virtual environment
& $venvActivate

# Step 2: Install Python Dependencies
Write-Host "[2/5] Installing Python dependencies..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    pip install -q -r requirements.txt
    Write-Host "      Python dependencies installed successfully." -ForegroundColor Green
} else {
    Write-Host "ERROR: requirements.txt not found." -ForegroundColor Red
    exit 1
}

# Step 3: Build React Frontend
Write-Host "[3/5] Preparing React frontend..." -ForegroundColor Yellow
if (Test-Path $frontendDir) {
    Set-Location $frontendDir
    
    if (Test-Path "package.json") {
        if (-Not (Test-Path "dist")) {
            Write-Host "      Installing Node.js dependencies..." -ForegroundColor Gray
            npm install --silent 2>&1 | Out-Null
            if ($LASTEXITCODE -ne 0) {
                Write-Host "ERROR: Failed to install Node.js dependencies." -ForegroundColor Red
                Set-Location $root
                exit 1
            }
            
            Write-Host "      Building React frontend..." -ForegroundColor Gray
            npm run build --silent 2>&1 | Out-Null
            if ($LASTEXITCODE -ne 0) {
                Write-Host "ERROR: Failed to build frontend." -ForegroundColor Red
                Set-Location $root
                exit 1
            }
            Write-Host "      Frontend built successfully." -ForegroundColor Green
        } else {
            Write-Host "      Frontend already built." -ForegroundColor Green
        }
    }
    Set-Location $root
}

# Step 4: Verify Project Structure
Write-Host "[4/5] Verifying project structure..." -ForegroundColor Yellow
$checks = @(
    @("Frontend dist", "./frontend/dist/index.html"),
    @("Backend routes", "./app/routes.py"),
    @("Database models", "./app/models.py"),
    @("ML model", "./model/model.pkl")
)

foreach ($check in $checks) {
    if (Test-Path $check[1]) {
        Write-Host "      [OK] $($check[0])" -ForegroundColor Green
    } else {
        Write-Host "      [WARN] $($check[0]) - Missing" -ForegroundColor Yellow
    }
}

# Step 5: Start Flask Server
Write-Host "[5/5] Starting Flask server..." -ForegroundColor Yellow
Write-Host ""

# Start Flask as a background job
$flaskJob = Start-Job -ScriptBlock {
    cd $args[0]
    python run.py
} -ArgumentList $root

# Wait for server to start
Write-Host "      Waiting for server to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 3

# Check if server is running
$serverReady = $false
for ($i = 0; $i -lt 10; $i++) {
    try {
        $response = Invoke-WebRequest -Uri http://localhost:5000 -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $serverReady = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "                   PROJECT READY TO USE" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""
Write-Host ">> Server running at http://localhost:5000" -ForegroundColor Green
Write-Host ""
Write-Host "Demo Credentials:" -ForegroundColor Cyan
Write-Host "   - admin / Admin@1234" -ForegroundColor Gray
Write-Host "   - inspector / Inspect2026!" -ForegroundColor Gray
Write-Host "   - newsreader / ReadNews!23" -ForegroundColor Gray
Write-Host ""
Write-Host "API Documentation:" -ForegroundColor Cyan
Write-Host "   - Main: http://localhost:5000/api/" -ForegroundColor Gray
Write-Host "   - Health: http://localhost:5000/api/health" -ForegroundColor Gray
Write-Host ""

# Open browser automatically
Write-Host ">> Opening browser..." -ForegroundColor Yellow
Start-Sleep -Seconds 1
Start-Process "http://localhost:5000"

Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Keep script running and monitor Flask job
while ($true) {
    if ($flaskJob.State -eq "Failed") {
        Write-Host "Flask server encountered an error. Exiting..." -ForegroundColor Red
        break
    }
    Start-Sleep -Seconds 1
}
