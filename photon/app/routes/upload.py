import base64
import os
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.services import upload_store

router = APIRouter()

_ALLOWED = {'.csv', '.xlsx', '.xls'}


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in _ALLOWED:
        return JSONResponse(
            status_code=400,
            content={"error": f"File type {ext} not supported. Use CSV or Excel."},
        )

    contents = await file.read()
    upload_id = str(uuid.uuid4())
    upload_store.put(upload_id, {
        "content": base64.b64encode(contents).decode(),
        "filename": file.filename,
        "extension": ext,
    })

    return {"path": f"photon-upload://{upload_id}", "filename": file.filename}


@router.get("/retrieve/{upload_id}")
async def retrieve_upload(upload_id: str):
    if not upload_store.contains(upload_id):
        raise HTTPException(status_code=404, detail="Upload not found or expired")
    return upload_store.get(upload_id)
