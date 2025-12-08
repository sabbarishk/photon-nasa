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
        
        # Get venv path
        venv_path = Path(sys.executable).parent.parent
        activate_script = venv_path / "Scripts" / "activate.bat"
        
        print(f"🔍 DEBUG: Venv path: {venv_path}")
        print(f"🔍 DEBUG: Activate script exists: {activate_script.exists()}")
        
        # Create temporary directory for execution
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write code to file
            code_file = Path(tmpdir) / "notebook_code.py"
            
            # Modify code to save plots instead of showing them
            modified_code = req.code.replace("plt.show()", "")
            modified_code += "\n\n# Save all figures\nimport matplotlib.pyplot as plt\nfig_num = 1\nfor fig in [plt.figure(n) for n in plt.get_fignums()]:\n    fig.savefig(f'output_fig_{fig_num}.png', dpi=150, bbox_inches='tight')\n    fig_num += 1\nplt.close('all')\n"
            
            code_file.write_text(modified_code, encoding='utf-8')
            
            # Execute with venv activation if on Windows
            if activate_script.exists():
                # Create a batch file that activates venv and runs Python
                batch_file = Path(tmpdir) / "run_code.bat"
                batch_content = f'''@echo off
call "{activate_script}"
cd /d "{tmpdir}"
"{python_executable}" "{code_file}"
'''
                batch_file.write_text(batch_content, encoding='utf-8')
                
                result = subprocess.run(
                    [str(batch_file)],
                    cwd=tmpdir,
                    capture_output=True,
                    text=True,
                    timeout=req.timeout,
                    shell=True
                )
            else:
                # Fallback: comprehensive environment setup
                env = os.environ.copy()
                import site
                
                # Add all possible paths
                paths_to_add = []
                paths_to_add.extend(site.getsitepackages())
                paths_to_add.extend(sys.path)
                
                # Add venv's Lib and site-packages explicitly
                venv_lib = venv_path / "Lib"
                venv_site = venv_path / "Lib" / "site-packages"
                if venv_lib.exists():
                    paths_to_add.append(str(venv_lib))
                if venv_site.exists():
                    paths_to_add.append(str(venv_site))
                
                # Set PYTHONPATH
                existing_path = env.get('PYTHONPATH', '')
                all_paths = [p for p in paths_to_add if p] + ([existing_path] if existing_path else [])
                env['PYTHONPATH'] = os.pathsep.join(all_paths)
                
                print(f"🔍 DEBUG: PYTHONPATH set to: {env['PYTHONPATH'][:200]}...")
                
                result = subprocess.run(
                    [python_executable, str(code_file)],
                    cwd=tmpdir,
                    env=env,
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
