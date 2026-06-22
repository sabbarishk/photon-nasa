from fastapi import APIRouter
from pydantic import BaseModel

from app.services import vector_db

router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


@router.post("/")
def search(req: QueryRequest):
    results = vector_db.search(req.query, top_k=req.top_k)
    return {"query": req.query, "results": results}
