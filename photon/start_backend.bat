@echo off
cd /d "D:\Photon\photon_initial\photon"
call venv\Scripts\activate.bat
set PHOTON_SKIP_AUTH=1
echo Starting Photon backend on http://127.0.0.1:8001
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
