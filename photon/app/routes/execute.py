import base64
import os
import subprocess
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

SANDBOX_IMAGE = "photon-sandbox"
TIMEOUT_SECONDS = 15
MEMORY_LIMIT = "256m"
CPU_LIMIT = "0.5"

# Force non-interactive matplotlib backend before any user code runs.
_PREAMBLE = (
    "import matplotlib\n"
    "matplotlib.use('Agg')\n"
)

# Replaces plt.show() so figures are written to disk and returned to the caller.
_SAVEFIG_SNIPPET = (
    "\nimport matplotlib.pyplot as _plt\n"
    "_fig = _plt.gcf()\n"
    "if _fig is not None and len(_fig.get_axes()) > 0:\n"
    "    _fig.savefig('/workspace/output_fig_1.png', dpi=150, bbox_inches='tight')\n"
)


class ExecuteRequest(BaseModel):
    code: str


def _docker_available() -> bool:
    try:
        r = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=5,
        )
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _prepare_code(user_code: str) -> str:
    return _PREAMBLE + user_code.replace("plt.show()", _SAVEFIG_SNIPPET)


@router.post("/notebook")
def execute_notebook(req: ExecuteRequest):
    if not _docker_available():
        raise HTTPException(
            status_code=503,
            detail=(
                "Code execution unavailable: Docker is not running on this host. "
                "Start Docker Desktop (or the Docker daemon) and retry."
            ),
        )

    container_name = f"photon-exec-{uuid.uuid4().hex[:12]}"

    with tempfile.TemporaryDirectory() as tmpdir:
        code_path = os.path.join(tmpdir, "code.py")
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(_prepare_code(req.code))

        cmd = [
            "docker", "run",
            "--rm",
            "--name", container_name,
            "--network", "none",
            "--memory", MEMORY_LIMIT,
            "--cpus", CPU_LIMIT,
            "--volume", f"{tmpdir}:/workspace",
            SANDBOX_IMAGE,
            "python", "/workspace/code.py",
        ]

        stdout = ""
        stderr = ""
        exit_code = 1
        timed_out = False

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
            )
            stdout = result.stdout
            stderr = result.stderr
            exit_code = result.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            stderr = f"Hard timeout: execution exceeded {TIMEOUT_SECONDS}s and was killed."
            subprocess.run(["docker", "kill", container_name], capture_output=True)
        except FileNotFoundError:
            raise HTTPException(
                status_code=503,
                detail="Docker executable not found. Is Docker installed and on PATH?",
            )

        images = []
        for img_file in sorted(Path(tmpdir).glob("*.png")):
            with open(img_file, "rb") as f:
                img_data = base64.b64encode(f.read()).decode("utf-8")
                images.append({
                    "filename": img_file.name,
                    "data": f"data:image/png;base64,{img_data}",
                })

        return {
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": exit_code,
            "timed_out": timed_out,
            "images": images,
        }
