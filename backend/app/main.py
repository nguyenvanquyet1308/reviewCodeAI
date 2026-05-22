from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import engine, Base
import app.db.base  # noqa: F401
from app.api.routes import health, webhooks, reviews, repositories

# Initialize logging configuration
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database tables exist
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="Automated AI GitHub Code Review Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS config to support React frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register endpoints
app.include_router(health.router, prefix="/api/health", tags=["Health"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["Reviews"])
app.include_router(repositories.router, prefix="/api/repositories", tags=["Repositories"])
