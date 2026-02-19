param(
    [switch]$SkipAuth,
    [int]$Port = 8000,
    [switch]$Reload
)

# Activate venv if present
$venvActivate = Join-Path (Get-Location) ".venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    Write-Host "Activating venv..."
    & $venvActivate
} else {
    Write-Host "No .venv found. Ensure your Python environment is active or create one with: python -m venv .venv"
}

if ($SkipAuth) {
    Write-Host "Starting server with PHOTON_SKIP_AUTH=1 (development)."
    $env:PHOTON_SKIP_AUTH = '1'
}

Write-Host "Using port $Port"
$python = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { $python = "python" }

if ($Reload) {
    Write-Host "Running: $python -m uvicorn app.main:app --host 0.0.0.0 --reload --port $Port"
    & $python -m uvicorn app.main:app --host 0.0.0.0 --reload --port $Port
} else {
    Write-Host "Running: $python -m uvicorn app.main:app --host 0.0.0.0 --port $Port"
    & $python -m uvicorn app.main:app --host 0.0.0.0 --port $Port
}