from datetime import datetime
from sqlalchemy import String, Float, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Reading(Base):
    __tablename__ = "readings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    location_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    water_level_cm: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # "aman" | "waspada" | "bahaya"
    pixel_distance: Mapped[float | None] = mapped_column(Float, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    # Relasi
    location: Mapped["Location"] = relationship("Location", back_populates="readings")
    alert: Mapped["Alert | None"] = relationship(
        "Alert", back_populates="reading", uselist=False
    )

    def __repr__(self) -> str:
        return f"<Reading id={self.id} level={self.water_level_cm}cm status={self.status}>"
