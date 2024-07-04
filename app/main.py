from fastapi import FastAPI
from contextlib import asynccontextmanager

from api.extract.router import router as v1_extract_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("startup event")
    yield
    print("shutdown event")
    
    
app = FastAPI(
    lifespan=lifespan,
    title="simple-url-extractor API",
    description="""
""",
    servers=[],
    version="0.0.1",
)

app.include_router(v1_extract_router, prefix="/v1")
