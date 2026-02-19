from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import nbformat
from nbformat.v4 import new_notebook, new_code_cell
from pathlib import Path
from jinja2 import Template
from uuid import uuid4
import logging

router = APIRouter()
log = logging.getLogger(__name__)


class WorkflowRequest(BaseModel):
    dataset_url: str
    dataset_format: str
    variable: str
    title: str = "Generated Workflow"


@router.post("/generate")
async def generate_workflow(request: WorkflowRequest):
    """Generate analysis workflow from template"""
    try:
        template_path = Path(__file__).parent.parent / "templates" / f"{request.dataset_format.lower()}.txt"

        if not template_path.exists():
            raise HTTPException(status_code=400, detail=f"No template for format: {request.dataset_format}")

        with open(template_path, "r", encoding="utf-8") as f:
            template_str = f.read()

        template = Template(template_str)
        code = template.render(
            dataset_url=request.dataset_url,
            variable=request.variable,
            title=request.title
        )

        # ← ADD THIS: Strip BOM and other invisible characters
        code = code.lstrip('\ufeff\ufbf0\ufbf1\ufbf2')  # Remove UTF-8/16/32 BOM
        code = code.strip()  # Remove leading/trailing whitespace

        notebook = {
            "cells": [
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "id": str(uuid4())[:8],
                    "metadata": {},
                    "outputs": [],
                    "source": code.split('\n')  # nbformat expects list of lines
                }
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 5
        }

        return {
            "notebook": notebook,
            "preview": code[:500],
            "format": request.dataset_format
        }

    except Exception as e:
        log.error(f"Workflow generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate workflow: {str(e)}")
