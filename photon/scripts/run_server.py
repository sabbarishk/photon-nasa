
"""Start the FastAPI app programmatically to avoid uvicorn import path issues.

Run: python <absolute-path-to>/scripts/run_server.py
"""
import os
import sys

# Ensure the project root (parent of this scripts/ folder) is first on sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from uvicorn import run


if __name__ == "__main__":
    run("app.main:app", host="127.0.0.1", port=8000)
