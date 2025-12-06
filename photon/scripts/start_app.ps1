# start_app.ps1
# PowerShell helper to free port 8000 (if used) and run the FastAPI app.
# Run from project root: .\scripts\start_app.ps1

# Find processes listening on :8000 and kill them
$matches = netstat -ano | Select-String ':8000'
if ($matches) {
    Write-Host 'Found processes using port 8000; attempting to stop them...'
    foreach ($m in $matches) {
        $parts = ($m -replace '\s+', ' ') -split ' '
        $pid = $parts[-1]
        if ($pid -and ($pid -as [int] -gt 0)) {
            try {
                Write-Host "Stopping PID $pid"
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            } catch {
                Write-Host "Could not stop PID $pid: $_"
            }
        }
    }
    Start-Sleep -Seconds 1
} else {
    Write-Host 'No process found on port 8000.'
}

# Set PYTHONPATH so 'app' package is importable
$env:PYTHONPATH = (Get-Location).Path

Write-Host 'Starting FastAPI (uvicorn) on http://127.0.0.1:8000'
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
