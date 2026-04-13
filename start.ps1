$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontendDir = Join-Path $root 'frontend'
$venvPython = Join-Path $root '.venv\Scripts\python.exe'

function Write-Step($message) {
    Write-Host ""
    Write-Host "==> $message" -ForegroundColor Cyan
}

function Test-AppReady {
    try {
        $response = Invoke-WebRequest -Uri 'http://127.0.0.1:5000/api/health' -UseBasicParsing -TimeoutSec 2
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

Set-Location $root

Write-Host "TruthLens launcher" -ForegroundColor Green
Write-Host "Workspace: $root" -ForegroundColor DarkGray

Write-Step "Checking Python environment"
if (-not (Test-Path $venvPython)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
& $venvPython -m pip install -q -r requirements.txt

Write-Step "Preparing frontend"
if (Test-Path (Join-Path $frontendDir 'package.json')) {
    Set-Location $frontendDir
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    npm install --silent
    Write-Host "Building frontend..." -ForegroundColor Yellow
    npm run build --silent
    Set-Location $root
}

Write-Step "Starting server"
$existing = Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($existing) {
    Write-Host "Stopping existing server on port 5000..." -ForegroundColor Yellow
    Stop-Process -Id $existing.OwningProcess -Force
    Start-Sleep -Seconds 2
}

$server = Start-Process -FilePath $venvPython -ArgumentList 'run.py' -WorkingDirectory $root -WindowStyle Hidden -PassThru

$ready = $false
for ($i = 0; $i -lt 15; $i++) {
    Start-Sleep -Seconds 1
    if (Test-AppReady) {
        $ready = $true
        break
    }
}

if (-not $ready) {
    Write-Host "TruthLens did not start successfully." -ForegroundColor Red
    Write-Host "Process id: $($server.Id)" -ForegroundColor DarkGray
    exit 1
}

Write-Host ""
Write-Host "TruthLens is running." -ForegroundColor Green
Write-Host "App: http://localhost:5000" -ForegroundColor Green
Write-Host "API docs: http://localhost:5000/api/" -ForegroundColor Green
Write-Host ""
Write-Host "Demo accounts:" -ForegroundColor Cyan
Write-Host "  admin@truthguard.ai / Admin@1234"
Write-Host "  inspector@truthguard.ai / Inspect2026!"
Write-Host "  reader@truthguard.ai / ReadNews!23"
Write-Host ""
Write-Host "Server PID: $($server.Id)" -ForegroundColor DarkGray

Start-Process 'http://localhost:5000'
