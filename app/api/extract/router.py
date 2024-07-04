from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ExtractResponse(BaseModel):
    title: Optional[str]
    author: Optional[str]
    hostname: Optional[str]
    date: Optional[str]
    fingerprint: Optional[str]
    id: Optional[str]
    license: Optional[str]
    comments: Optional[str]
    raw_text: Optional[str]
    text: Optional[str]
    language: Optional[str]
    image: Optional[str]
    pagetype: Optional[str]
    filedate: Optional[str]
    source: Optional[str]
    source_hostname: Optional[str]
    excerpt: Optional[str]
    categories: Optional[str]
    tags: Optional[str]

@router.get(
    "/extract",
    tags=['Extract'],
    operation_id="extract",
    summary="extract url",
    response_model=ExtractResponse
)
async def v1_route(url: str, cache_seconds: int = 600):
    """
    Extract information from the given URL.
    """
    from libs.extractor import extract
    try:
        return await extract(url=url, cache_seconds=cache_seconds)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )
