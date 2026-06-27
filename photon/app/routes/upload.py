import os
import shutil
import uuid

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

router = APIRouter()

_ALLOWED = {'.csv', '.xlsx', '.xls'}
_UPLOAD_DIR = '/tmp/photon_uploads'


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in _ALLOWED:
        return JSONResponse(
            status_code=400,
            content={"error": f"File type {ext} not supported. Use CSV or Excel."},
        )

    os.makedirs(_UPLOAD_DIR, exist_ok=True)
    safe_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(_UPLOAD_DIR, safe_name)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {"path": file_path, "filename": file.filename}
