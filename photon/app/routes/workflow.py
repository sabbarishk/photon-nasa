import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

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
    """Profile → retrieve methodology → generate analysis code.

    Does NOT execute the code — call /execute separately with the
    returned code string.
    """
    try:
        df = load_dataframe(req.source)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.error("Failed to load data from %s: %s", req.source, e)
        raise HTTPException(status_code=400, detail=f"Could not load data: {e}")

    data_profile = profile(df)
    playbook = search_playbooks(data_profile["data_type"])

    try:
        code = generate_analysis_code(req.question, data_profile, playbook, req.source)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        log.error("LLM generation failed: %s", e)
        raise HTTPException(status_code=500, detail="Code generation failed")

    return {
        "code": code,
        "profile": data_profile,
        "methodology_used": data_profile["data_type"],
    }
