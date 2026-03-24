from sqlalchemy import String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class CropAdvisory(Base):
    __tablename__ = "crop_advisories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    crop: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    pest_disease: Mapped[str] = mapped_column(String(200), nullable=False)
    symptoms_te: Mapped[str | None] = mapped_column(Text, nullable=True)
    symptoms_hi: Mapped[str | None] = mapped_column(Text, nullable=True)
    symptoms_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    treatment: Mapped[str] = mapped_column(Text, nullable=False)
    treatment_te: Mapped[str | None] = mapped_column(Text, nullable=True)
    treatment_hi: Mapped[str | None] = mapped_column(Text, nullable=True)
    dosage: Mapped[str | None] = mapped_column(String(500), nullable=True)
    urgency: Mapped[str] = mapped_column(String(20), default="medium")  # low, medium, high, critical
    source: Mapped[str | None] = mapped_column(String(200), nullable=True)
