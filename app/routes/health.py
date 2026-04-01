import logging
import time

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import VERSION
from app.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health(db: Session = Depends(get_db)):
    """Health check that verifies database connectivity."""
    start = time.monotonic()
    try:
        db.execute(text("SELECT 1"))
        duration_ms = (time.monotonic() - start) * 1000
        return {
            "status": "healthy",
            "version": VERSION,
            "database": "connected",
            "db_response_ms": round(duration_ms, 1),
        }
    except Exception:
        duration_ms = (time.monotonic() - start) * 1000
        logger.exception("Health check failed: database unreachable")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "version": VERSION,
                "database": "unreachable",
                "db_response_ms": round(duration_ms, 1),
            },
        )
