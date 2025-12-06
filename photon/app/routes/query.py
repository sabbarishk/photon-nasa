from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

from app.services.hf_api import get_embedding
from app.services.vector_store import VectorStore

router = APIRouter()
vs = VectorStore("data/vectors.json")


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


@router.post("/")
def search(req: QueryRequest):
    emb = get_embedding(req.query)
    results = vs.search(emb, top_k=req.top_k)
    return {"query": req.query, "results": results}
