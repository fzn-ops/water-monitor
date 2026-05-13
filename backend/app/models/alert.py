from datetime import datetime
from sqlalchemy import String, Integer, Boolean, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    reading_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("readings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relasi
    reading: Mapped["Reading"] = relationship("Reading", back_populates="alert")

    def __repr__(self) -> str:
        return f"<Alert id={self.id} sent={self.is_sent}>"
