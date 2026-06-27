import json
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.lambda_executor import execute_via_lambda
from app.services.llm import (
    generate_analysis_code,
    generate_follow_up_suggestions,
    generate_insight_narrative,
)
from app.services.profiler import load_dataframe, profile
from app.services.vector_db import search_playbooks

router = APIRouter()
log = logging.getLogger(__name__)


class WorkflowRequest(BaseModel):
    question: str
    source: str
    conversation_history: list = []
    session_id: str = ""


def _parse_summary(stdout: str) -> tuple:
    """Extract KPI cards and anomalies from the PHOTON_SUMMARY marker in stdout."""
    if not stdout or "PHOTON_SUMMARY:" not in stdout:
        return [], []
    try:
        json_str = stdout.split("PHOTON_SUMMARY:")[1].strip()
        summary = json.loads(json_str)
        return summary.get("kpis", []), summary.get("anomalies", [])
    except Exception:
        return [], []


@router.post("/generate")
def generate_workflow(req: WorkflowRequest):
    # Step 1: load and profile the data.
    try:
        df = load_dataframe(req.source)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.error("Failed to load data from %s: %s", req.source, e)
        raise HTTPException(status_code=400, detail=f"Could not load data: {e}")

    data_profile = profile(df)

    # Step 2: retrieve methodology playbook.
    playbook = search_playbooks(data_profile["data_type"])

    # Step 3: generate dashboard code grounded in profile + playbook + history.
    try:
        code = generate_analysis_code(
            req.question,
            data_profile,
            playbook,
            req.source,
            req.conversation_history,
        )
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        log.error("LLM generation failed: %s", e)
        raise HTTPException(status_code=500, detail="Code generation failed")

    # Step 4: execute in Lambda sandbox.
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

    execution_result = {
        "stdout": execution.get("stdout", ""),
        "stderr": execution.get("stderr", ""),
        "exit_code": execution.get("exit_code", 1),
        "output_image": execution.get("output_image"),
    }

    # Step 5: parse KPIs and anomalies from PHOTON_SUMMARY marker in stdout.
    kpi_cards, anomalies = [], []
    if execution_result["exit_code"] == 0:
        kpi_cards, anomalies = _parse_summary(execution_result["stdout"])

    # Step 6: generate insight narrative (second LLM pass, only on success).
    insight_narrative = ""
    if execution_result["exit_code"] == 0:
        insight_narrative = generate_insight_narrative(
            req.question,
            data_profile,
            kpi_cards,
            anomalies,
            req.conversation_history,
        )

    # Step 7: generate follow-up suggestions (third LLM call).
    follow_up_suggestions = generate_follow_up_suggestions(
        req.question,
        data_profile,
        kpi_cards,
    )

    return {
        "code": code,
        "profile": data_profile,
        "methodology_used": data_profile["data_type"],
        "execution": execution_result,
        "kpi_cards": kpi_cards,
        "anomalies": anomalies,
        "insight_narrative": insight_narrative,
        "follow_up_suggestions": follow_up_suggestions,
    }
