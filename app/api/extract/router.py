from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get(
    "/extract",
    tags=['Extract'],
    operation_id="extract",
    summary="extract url",
)
async def v1_route(url: str, cache_seconds: int = 600):
    """
    """
    from libs.extractor import extract
    try :
        return await extract(url=url, cache_seconds=cache_seconds)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}")
