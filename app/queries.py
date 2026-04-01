"""Reusable database queries."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Product, Score, Tag
from app.models.score import ALL_CAPABILITY_FIELDS


def get_active_product(db: Session, product_id: int, options=None) -> Product | None:
    """Get an active product by ID, or None."""
    query = db.query(Product).filter(
        Product.id == product_id, Product.is_active.is_(True)
    )
    if options:
        query = query.options(*options)
    return query.first()


def get_tag(db: Session, tag_id: int, product_id: int) -> Tag | None:
    """Get a tag by ID belonging to a product, or None."""
    return db.query(Tag).filter(Tag.id == tag_id, Tag.product_id == product_id).first()


def get_org_summary(db: Session):
    """Get org-wide averages for all latest scores of active products."""
    return db.query(
        *[func.avg(getattr(Score, f)).label(f) for f in ALL_CAPABILITY_FIELDS],
        *[func.avg(getattr(Score, cat)).label(cat) for cat in ["a", "b", "c", "d", "e"]],
        func.avg(Score.total).label("total"),
    ).join(Product).filter(Score.latest.is_(True), Product.is_active.is_(True)).first()
