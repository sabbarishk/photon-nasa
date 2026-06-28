from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

_DEMO_CSV = Path(__file__).parent.parent.parent / "data" / "demo" / "manufacturing_quality.csv"


@router.get("/manufacturing")
def get_demo_dataset():
    if not _DEMO_CSV.exists():
        raise HTTPException(status_code=404, detail="Demo dataset not found. Run photon/scripts/generate_demo_data.py first.")
    return FileResponse(
        path=str(_DEMO_CSV),
        media_type="text/csv",
        filename="manufacturing_quality.csv",
    )
