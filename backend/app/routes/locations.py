from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.location import Location
from app.schemas.location import LocationCreate, LocationUpdate, LocationResponse

router = APIRouter()


@router.get("/", response_model=list[LocationResponse])
async def get_all_locations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Ambil semua lokasi monitoring."""
    result = await db.execute(select(Location).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{location_id}", response_model=LocationResponse)
async def get_location(
    location_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Ambil satu lokasi berdasarkan ID."""
    result = await db.execute(select(Location).where(Location.id == location_id))
    location = result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lokasi tidak ditemukan")
    return location


@router.post("/", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_location(
    payload: LocationCreate,
    db: AsyncSession = Depends(get_db),
):
    """Tambah lokasi monitoring baru."""
    location = Location(**payload.model_dump())
    db.add(location)
    await db.flush()
    await db.refresh(location)
    return location


@router.patch("/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: int,
    payload: LocationUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update data lokasi."""
    result = await db.execute(select(Location).where(Location.id == location_id))
    location = result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lokasi tidak ditemukan")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(location, field, value)

    await db.flush()
    await db.refresh(location)
    return location


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Hapus lokasi (beserta readings & alerts terkait)."""
    result = await db.execute(select(Location).where(Location.id == location_id))
    location = result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lokasi tidak ditemukan")

    await db.delete(location)
