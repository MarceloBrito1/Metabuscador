from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import auth, search
from app.logger import get_logger

logger = get_logger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Metabuscador API",
    description="Meta-search engine API that aggregates results from multiple search engines",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:80", "http://frontend"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(search.router, prefix="/api")

@app.get("/api/health")
def health():
    return {"status": "ok"}

logger.info("Metabuscador API started")
