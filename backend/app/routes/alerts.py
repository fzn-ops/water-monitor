from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertResponse

router = APIRouter()


@router.get("/", response_model=list[AlertResponse])
async def get_all_alerts(
    is_sent: bool | None = Query(None, description="Filter: sudah terkirim atau belum"),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Ambil semua log alert. Bisa filter berdasarkan status pengiriman."""
    query = select(Alert).order_by(Alert.created_at.desc()).offset(skip).limit(limit)
    if is_sent is not None:
        query = query.where(Alert.is_sent == is_sent)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Ambil satu alert berdasarkan ID."""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert tidak ditemukan")
    return alert
