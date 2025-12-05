from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.app.core.database import get_db

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    # БД
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    # Файловое хранилище
    storage_status = "unhealthy"
    try:
        base = Path("file_storage")
        base.mkdir(parents=True, exist_ok=True)
        probe = base / ".health_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        storage_status = "healthy"
    except Exception:
        storage_status = "unhealthy"

    status_ = "healthy" if db_status == "healthy" and storage_status == "healthy" else "unhealthy"
    return {
        "status": status_,
        "database": db_status,
        "storage": storage_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
