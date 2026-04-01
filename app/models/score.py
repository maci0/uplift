from datetime import datetime
from sqlalchemy import CheckConstraint, Index, Integer, Float, Boolean, Text, DateTime, ForeignKey, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

# All capability field names grouped by category
CATEGORY_FIELDS = {
    "a": [f"a{i}" for i in range(1, 13)],  # a1-a12
    "b": [f"b{i}" for i in range(1, 9)],   # b1-b8
    "c": [f"c{i}" for i in range(1, 11)],  # c1-c10
    "d": [f"d{i}" for i in range(1, 9)],   # d1-d8
    "e": [f"e{i}" for i in range(1, 5)],   # e1-e4
}

ALL_CAPABILITY_FIELDS = []
for fields in CATEGORY_FIELDS.values():
    ALL_CAPABILITY_FIELDS.extend(fields)


class Score(Base):
    __tablename__ = "scores"
    __table_args__ = (
        Index("ix_scores_product_id_latest", "product_id", "latest"),
        Index(
            "uq_scores_one_latest_per_product",
            "product_id",
            unique=True,
            sqlite_where=text("latest = 1"),
            postgresql_where=text("latest = true"),
        ),
        *(
            CheckConstraint(
                f"{f} IS NULL OR ({f} >= 1 AND {f} <= 4)",
                name=f"ck_scores_{f}_range",
            )
            for f in ALL_CAPABILITY_FIELDS
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)

    # Category A: Code (12 capabilities)
    a1: Mapped[int | None] = mapped_column(Integer, nullable=True)
    a2: Mapped[int | None] = mapped_column(Integer, nullable=True)
    a3: Mapped[int | None] = mapped_column(Integer, nullable=True)
    a4: Mapped[int | None] = mapped_column(Integer, nullable=True)
    a5: Mapped[int | None] = mapped_column(Integer, nullable=True)
    a6: Mapped[int | None] = mapped_column(Integer, nullable=True)
    a7: Mapped[int | None] = mapped_column(Integer, nullable=True)
    a8: Mapped[int | None] = mapped_column(Integer, nullable=True)
    a9: Mapped[int | None] = mapped_column(Integer, nullable=True)
    a10: Mapped[int | None] = mapped_column(Integer, nullable=True)
    a11: Mapped[int | None] = mapped_column(Integer, nullable=True)
    a12: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Category B: Build & Test (8 capabilities)
    b1: Mapped[int | None] = mapped_column(Integer, nullable=True)
    b2: Mapped[int | None] = mapped_column(Integer, nullable=True)
    b3: Mapped[int | None] = mapped_column(Integer, nullable=True)
    b4: Mapped[int | None] = mapped_column(Integer, nullable=True)
    b5: Mapped[int | None] = mapped_column(Integer, nullable=True)
    b6: Mapped[int | None] = mapped_column(Integer, nullable=True)
    b7: Mapped[int | None] = mapped_column(Integer, nullable=True)
    b8: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Category C: Release (10 capabilities)
    c1: Mapped[int | None] = mapped_column(Integer, nullable=True)
    c2: Mapped[int | None] = mapped_column(Integer, nullable=True)
    c3: Mapped[int | None] = mapped_column(Integer, nullable=True)
    c4: Mapped[int | None] = mapped_column(Integer, nullable=True)
    c5: Mapped[int | None] = mapped_column(Integer, nullable=True)
    c6: Mapped[int | None] = mapped_column(Integer, nullable=True)
    c7: Mapped[int | None] = mapped_column(Integer, nullable=True)
    c8: Mapped[int | None] = mapped_column(Integer, nullable=True)
    c9: Mapped[int | None] = mapped_column(Integer, nullable=True)
    c10: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Category D: Operate (8 capabilities)
    d1: Mapped[int | None] = mapped_column(Integer, nullable=True)
    d2: Mapped[int | None] = mapped_column(Integer, nullable=True)
    d3: Mapped[int | None] = mapped_column(Integer, nullable=True)
    d4: Mapped[int | None] = mapped_column(Integer, nullable=True)
    d5: Mapped[int | None] = mapped_column(Integer, nullable=True)
    d6: Mapped[int | None] = mapped_column(Integer, nullable=True)
    d7: Mapped[int | None] = mapped_column(Integer, nullable=True)
    d8: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Category E: Optimize (4 capabilities)
    e1: Mapped[int | None] = mapped_column(Integer, nullable=True)
    e2: Mapped[int | None] = mapped_column(Integer, nullable=True)
    e3: Mapped[int | None] = mapped_column(Integer, nullable=True)
    e4: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Computed category averages
    a: Mapped[float | None] = mapped_column(Float, nullable=True)
    b: Mapped[float | None] = mapped_column(Float, nullable=True)
    c: Mapped[float | None] = mapped_column(Float, nullable=True)
    d: Mapped[float | None] = mapped_column(Float, nullable=True)
    e: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Overall score
    total: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Metadata
    latest: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    product = relationship("Product", back_populates="scores")

    def get_capability_array(self) -> list[int]:
        return [getattr(self, f, 0) or 0 for f in ALL_CAPABILITY_FIELDS]

    def get_category_array(self) -> list[float]:
        return [self.a or 0, self.b or 0, self.c or 0, self.d or 0, self.e or 0]

    def compute_totals(self, capabilities: dict) -> None:
        """Compute category averages and cloud readiness score.

        Sets self.a-e to category averages, self.total to the percentage (0-100)
        of capabilities meeting their minimum threshold, and self.latest to True.
        """
        for cat_key, fields in CATEGORY_FIELDS.items():
            values = [getattr(self, f) for f in fields if getattr(self, f) is not None]
            if values:
                setattr(self, cat_key, sum(values) / len(values))
            else:
                setattr(self, cat_key, 0)

        # Compute total: percentage of capabilities meeting their minimum threshold
        mins = {
            k.replace("_min", ""): v
            for k, v in capabilities.items()
            if k.endswith("_min") and v is not None
        }
        if not mins:
            self.total = 0.0
        else:
            met = sum(
                1 for field, min_val in mins.items()
                if (val := getattr(self, field, None)) is not None and val >= min_val
            )
            self.total = (met / len(mins)) * 100

        self.latest = True
