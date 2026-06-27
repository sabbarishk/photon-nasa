import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.lambda_executor import execute_via_lambda

router = APIRouter()
log = logging.getLogger(__name__)

# Force non-interactive matplotlib backend before any user code runs.
_PREAMBLE = (
    "import matplotlib\n"
    "matplotlib.use('Agg')\n"
)

# If user code has an active figure but no explicit savefig call,
# save it to /tmp/output.png so Lambda picks it up automatically.
_SAVEFIG_SNIPPET = (
    "\nimport matplotlib.pyplot as _plt\n"
    "_fig = _plt.gcf()\n"
    "if _fig is not None and len(_fig.get_axes()) > 0:\n"
    "    _fig.savefig('/tmp/output.png', dpi=150, bbox_inches='tight')\n"
)


class ExecuteRequest(BaseModel):
    code: str


def _prepare_code(user_code: str) -> str:
    return _PREAMBLE + user_code.replace("plt.show()", _SAVEFIG_SNIPPET)


@router.post("/notebook")
def execute_notebook(req: ExecuteRequest):
    try:
        execution = execute_via_lambda(_prepare_code(req.code))
    except Exception as e:
        log.error("Lambda invocation failed: %s", e)
        raise HTTPException(
            status_code=503,
            detail=(
                "Code execution unavailable: could not reach Lambda. "
                "Check AWS credentials and network connectivity."
            ),
        )

    # Map Lambda's single output_image to the images[] list the API has always returned.
    raw_image = execution.get("output_image")
    images = []
    if raw_image:
        images.append({
            "filename": "output.png",
            "data": f"data:image/png;base64,{raw_image}",
        })

    return {
        "stdout": execution.get("stdout", ""),
        "stderr": execution.get("stderr", ""),
        "exit_code": execution.get("exit_code", 1),
        "timed_out": False,
        "images": images,
    }
