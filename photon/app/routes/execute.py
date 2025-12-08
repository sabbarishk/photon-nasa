from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import subprocess
import tempfile
import os
import base64
import json
import sys
from pathlib import Path

router = APIRouter()


class ExecuteRequest(BaseModel):
    code: str
    timeout: int = 60  # seconds


@router.post("/notebook")
def execute_notebook(req: ExecuteRequest):
    """
    Execute Python code from notebook and return outputs including images.
    Returns stdout, stderr, and base64-encoded images.
    """
    try:
        # Use the same Python executable that's running this FastAPI server
        python_executable = sys.executable
        print(f"🔍 DEBUG: Using Python: {python_executable}")
        print(f"🔍 DEBUG: Python version: {sys.version}")
        
        # Ensure subprocess uses the same environment
        env = os.environ.copy()
        # Add site-packages to PYTHONPATH
        import site
        site_packages = site.getsitepackages()
        if site_packages:
            env['PYTHONPATH'] = os.pathsep.join(site_packages + [env.get('PYTHONPATH', '')])
        
        # Create temporary directory for execution
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write code to file
            code_file = Path(tmpdir) / "notebook_code.py"
            
            # Modify code to save plots instead of showing them
            modified_code = req.code.replace("plt.show()", "")
            modified_code += "\n\n# Save all figures\nimport matplotlib.pyplot as plt\nfig_num = 1\nfor fig in [plt.figure(n) for n in plt.get_fignums()]:\n    fig.savefig(f'output_fig_{fig_num}.png', dpi=150, bbox_inches='tight')\n    fig_num += 1\nplt.close('all')\n"
            
            code_file.write_text(modified_code, encoding='utf-8')
            
            # Execute code using the same Python that runs this server (with all installed packages)
            result = subprocess.run(
                [python_executable, str(code_file)],
                cwd=tmpdir,
                env=env,  # Pass environment with PYTHONPATH
                capture_output=True,
                text=True,
                timeout=req.timeout
            )
            
            # Collect outputs
            output = {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "images": []
            }
            
            # Collect generated images
            for img_file in sorted(Path(tmpdir).glob("output_fig_*.png")):
                with open(img_file, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode('utf-8')
                    output["images"].append({
                        "filename": img_file.name,
                        "data": f"data:image/png;base64,{img_data}"
                    })
            
            # Also check for saved files
            for img_file in Path(tmpdir).glob("*.png"):
                if not img_file.name.startswith("output_fig_"):
                    with open(img_file, 'rb') as f:
                        img_data = base64.b64encode(f.read()).decode('utf-8')
                        output["images"].append({
                            "filename": img_file.name,
                            "data": f"data:image/png;base64,{img_data}"
                        })
            
            return output
            
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail=f"Execution timed out after {req.timeout} seconds")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")
