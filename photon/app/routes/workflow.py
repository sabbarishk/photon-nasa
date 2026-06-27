import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.lambda_executor import execute_via_lambda
from app.services.llm import generate_analysis_code
from app.services.profiler import load_dataframe, profile
from app.services.vector_db import search_playbooks

router = APIRouter()
log = logging.getLogger(__name__)


class WorkflowRequest(BaseModel):
    question: str
    source: str


@router.post("/generate")
def generate_workflow(req: WorkflowRequest):
    # Step 1-2: load and profile the data.
    try:
        df = load_dataframe(req.source)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.error("Failed to load data from %s: %s", req.source, e)
        raise HTTPException(status_code=400, detail=f"Could not load data: {e}")

    data_profile = profile(df)

    # Step 3: retrieve the methodology playbook for this data type.
    playbook = search_playbooks(data_profile["data_type"])

    # Step 4: generate analysis code grounded in profile + playbook.
    try:
        code = generate_analysis_code(req.question, data_profile, playbook, req.source)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        log.error("LLM generation failed: %s", e)
        raise HTTPException(status_code=500, detail="Code generation failed")

    # Step 5: execute in Lambda sandbox and return real results.
    try:
        execution = execute_via_lambda(code)
    except Exception as e:
        log.error("Lambda invocation failed: %s", e)
        raise HTTPException(
            status_code=503,
            detail=(
                "Code execution unavailable: could not reach Lambda. "
                "Check AWS credentials and network connectivity."
            ),
        )

    return {
        "code": code,
        "profile": data_profile,
        "methodology_used": data_profile["data_type"],
        "execution": {
            "stdout": execution.get("stdout", ""),
            "stderr": execution.get("stderr", ""),
            "exit_code": execution.get("exit_code", 1),
            "output_image": execution.get("output_image"),
        },
    }
