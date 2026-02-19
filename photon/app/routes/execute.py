from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import tempfile
import os
import base64
import sys
import io
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr

router = APIRouter()


class ExecuteRequest(BaseModel):
    code: str
    timeout: int = 60  # seconds


@router.get("/test-imports")
def test_imports():
    """Test what packages are available in this process"""
    results = {}
    test_packages = ['pandas', 'numpy', 'matplotlib', 'seaborn', 'xarray']
    
    for pkg in test_packages:
        try:
            module = __import__(pkg)
            results[pkg] = {
                'available': True,
                'version': getattr(module, '__version__', 'unknown'),
                'path': getattr(module, '__file__', 'unknown')
            }
        except ImportError as e:
            results[pkg] = {
                'available': False,
                'error': str(e)
            }
    
    results['sys.path'] = sys.path
    results['python_executable'] = sys.executable
    return results


@router.post("/notebook")
def execute_notebook(req: ExecuteRequest):
    """
    Execute Python code from notebook and return outputs including images.
    Returns stdout, stderr, and base64-encoded images.
    Uses exec() to run code in the same process with all packages available.
    """
    try:
        # Pre-import all common packages to make them available in exec namespace
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        
        # Try to import optional packages
        try:
            import seaborn as sns
        except ImportError:
            sns = None
            
        try:
            import xarray as xr
        except ImportError:
            xr = None
        
        # Create temporary directory for saving figures
        with tempfile.TemporaryDirectory() as tmpdir:
            # Capture stdout and stderr
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            # Save figure RIGHT BEFORE plt.show() while it's still alive
            save_code = f"""
import matplotlib.pyplot as plt
import os
fig = plt.gcf()
if fig and len(fig.get_axes()) > 0:
    fig.savefig(r'{tmpdir}/output_fig_1.png', dpi=150, bbox_inches='tight')
    print('[SAVED]')
"""
            # Inject save code before plt.show()
            modified_code = req.code.replace("plt.show()", save_code + "\nplt.show()")
            
            # Create execution namespace WITH pre-imported modules
            exec_globals = {
                '__name__': '__main__',
                '__file__': str(Path(tmpdir) / 'notebook_code.py'),
                'pd': pd,
                'pandas': pd,
                'np': np,
                'numpy': np,
                'plt': plt,
                'matplotlib': matplotlib,
                'sns': sns,
                'seaborn': sns,
                'xr': xr,
                'xarray': xr,
            }
            
            # Execute the code directly in this process
            exit_code = 0
            try:
                # Change to tmpdir for relative file operations
                original_cwd = os.getcwd()
                os.chdir(tmpdir)
                
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    exec(modified_code, exec_globals)
                    
                os.chdir(original_cwd)
            except Exception as e:
                exit_code = 1
                stderr_capture.write(f"\nExecution Error: {str(e)}\n")
                import traceback
                stderr_capture.write(traceback.format_exc())
                os.chdir(original_cwd)
            
            # Collect outputs
            output = {
                "stdout": stdout_capture.getvalue(),
                "stderr": stderr_capture.getvalue(),
                "exit_code": exit_code,
                "images": []
            }
            
            # Collect generated images
            for img_file in sorted(Path(tmpdir).glob("*.png")):
                with open(img_file, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode('utf-8')
                    output["images"].append({
                        "filename": img_file.name,
                        "data": f"data:image/png;base64,{img_data}"
                    })
            
            return output
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")
