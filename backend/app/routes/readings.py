from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.reading import Reading
from app.models.location import Location
from app.models.alert import Alert
from app.schemas.reading import ReadingCreate, ReadingResponse
from app.services.reading_service import determine_status

router = APIRouter()


@router.get("/", response_model=list[ReadingResponse])
async def get_all_readings(
    location_id: int | None = Query(None, description="Filter berdasarkan lokasi"),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Ambil semua data pembacaan level air. Bisa filter per lokasi."""
    query = select(Reading).order_by(Reading.recorded_at.desc()).offset(skip).limit(limit)
    if location_id:
        query = query.where(Reading.location_id == location_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/latest/{location_id}", response_model=ReadingResponse)
async def get_latest_reading(
    location_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Ambil pembacaan terbaru untuk suatu lokasi."""
    result = await db.execute(
        select(Reading)
        .where(Reading.location_id == location_id)
        .order_by(Reading.recorded_at.desc())
        .limit(1)
    )
    reading = result.scalar_one_or_none()
    if not reading:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Belum ada data pembacaan")
    return reading


@router.get("/{reading_id}", response_model=ReadingResponse)
async def get_reading(
    reading_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Ambil satu pembacaan berdasarkan ID."""
    result = await db.execute(select(Reading).where(Reading.id == reading_id))
    reading = result.scalar_one_or_none()
    if not reading:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data pembacaan tidak ditemukan")
    return reading


@router.post("/", response_model=ReadingResponse, status_code=status.HTTP_201_CREATED)
async def create_reading(
    payload: ReadingCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Tambah data pembacaan level air baru.
    Status (aman/waspada/bahaya) ditentukan otomatis.
    Jika status bahaya, alert otomatis dibuat.
    """
    # Validasi lokasi ada
    loc_result = await db.execute(select(Location).where(Location.id == payload.location_id))
    if not loc_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lokasi tidak ditemukan")

    # Tentukan status otomatis
    status_value = determine_status(payload.water_level_cm)

    reading = Reading(
        location_id=payload.location_id,
        water_level_cm=payload.water_level_cm,
        pixel_distance=payload.pixel_distance,
        status=status_value,
    )
    db.add(reading)
    await db.flush()  # dapat ID reading

    # Jika bahaya → buat alert otomatis
    if status_value == "bahaya":
        alert = Alert(
            reading_id=reading.id,
            message=(
                f"⚠️ BAHAYA! Tinggi air di lokasi ID {payload.location_id} "
                f"mencapai {payload.water_level_cm} cm."
            ),
            is_sent=False,
        )
        db.add(alert)

    await db.refresh(reading)
    return reading
