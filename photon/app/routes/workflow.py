from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import nbformat
from nbformat.v4 import new_notebook, new_code_cell

from app.services.hf_api import generate_code

router = APIRouter()


class WorkflowRequest(BaseModel):
    dataset_url: str
    dataset_format: str
    variable: str
    title: str = "Generated Workflow"


@router.post("/generate")
def generate(req: WorkflowRequest):
    # Load template for format
    tpl_path = os.path.join(os.path.dirname(__file__), '..', 'templates', f"{req.dataset_format.lower()}.txt")
    tpl_path = os.path.normpath(tpl_path)
    if not os.path.exists(tpl_path):
        # fallback to csv template
        tpl_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'templates', 'csv.txt'))

    with open(tpl_path, 'r', encoding='utf-8') as f:
        template = f.read()

    prompt = template.replace("{{ dataset_url }}", req.dataset_url).replace("{{ variable }}", req.variable).replace("{{ title }}", req.title)

    # Ask HF for extra polished code (optional); fallback to template code only
    try:
        code = generate_code(prompt)
    except Exception:
        code = prompt

    # Convert to a notebook
    try:
        nb = new_notebook(cells=[new_code_cell(code)])
        nb_json = nbformat.writes(nb)
        return {"notebook": nb_json}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Notebook creation failed: {e}")
