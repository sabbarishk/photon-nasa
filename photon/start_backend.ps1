# Start Photon Backend Server
$ErrorActionPreference = "Stop"

# Navigate to photon directory
Set-Location -Path "D:\Photon\photon_initial\photon"

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

# Set environment variable to skip auth
$env:PHOTON_SKIP_AUTH = "1"

# Start server
Write-Host "Starting Photon backend on http://127.0.0.1:8001" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
