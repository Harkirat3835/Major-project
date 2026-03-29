# Run both backend and frontend together in one step
# Usage: .\run_project.ps1

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontendDir = Join-Path $root 'frontend'
$venvPython = Join-Path $root '.venv\Scripts\python.exe'

if (-Not (Test-Path $venvPython)) {
    Write-Host 'Virtual environment Python not found at .venv\Scripts\python.exe' -ForegroundColor Yellow
    Write-Host 'Falling back to system python. Ensure the correct Python environment is active.'
    $venvPython = 'python'
}

Write-Host "Starting backend from: $root"
Start-Process powershell -ArgumentList "-NoExit", "-Command cd '$root'; & '.\.venv\Scripts\Activate.ps1'; python run.py" -WorkingDirectory $root

Write-Host "Starting frontend from: $frontendDir"
Start-Process powershell -ArgumentList "-NoExit", "-Command cd '$frontendDir'; npm run dev" -WorkingDirectory $frontendDir

Start-Sleep -Seconds 3
Write-Host 'Opening browser at http://localhost:5173'
Start-Process 'http://localhost:5173'

Write-Host 'Backend should be available at http://localhost:5000'
Write-Host 'Frontend should be available at http://localhost:5173'
