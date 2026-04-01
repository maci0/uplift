"""Seed the database with example data."""
import logging
import random
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Product, Score, Tag
from app.models.score import ALL_CAPABILITY_FIELDS
from app.capabilities import load_capabilities

logger = logging.getLogger("app.seed")

SAMPLE_PRODUCTS = [
    {
        "name": "Checkout API",
        "product_type": "Service",
        "url": "https://github.com/example/checkout-api",
        "description": "Payment processing service handling credit card transactions and order fulfillment.",
        "tags": [("team", "Payments"), ("environment", "production")],
        "assessments": [1, 2, 2, 3],
    },
    {
        "name": "Customer Portal",
        "product_type": "Application",
        "url": "https://github.com/example/customer-portal",
        "description": "Self-service web application for customers to manage accounts, view orders, and submit support tickets.",
        "tags": [("team", "Frontend"), ("environment", "production")],
        "assessments": [1, 1, 2, 3, 3],
    },
    {
        "name": "Inventory Service",
        "product_type": "Service",
        "url": "https://github.com/example/inventory-service",
        "description": "Real-time inventory tracking and warehouse management backend.",
        "tags": [("team", "Platform"), ("environment", "staging")],
        "assessments": [1, 2, 2],
    },
    {
        "name": "Analytics Pipeline",
        "product_type": "Service",
        "url": "https://github.com/example/analytics-pipeline",
        "description": "Event ingestion and data transformation pipeline feeding dashboards and reports.",
        "tags": [("team", "Data"), ("environment", "production")],
        "assessments": [2, 2, 3, 3],
    },
]


def _create_score(db: Session, product: Product, capabilities: dict, *, base_level: int = 1) -> Score:
    """Create a score with random capability values biased around base_level."""
    score = Score(product_id=product.id)
    for f in ALL_CAPABILITY_FIELDS:
        setattr(score, f, min(4, max(1, base_level + random.randint(-1, 1))))
    score.compute_totals(capabilities)
    db.add(score)
    return score


def seed_db():
    from app.config import settings
    if not settings.seed_db:
        logger.info("Seeding disabled (UPLIFT_SEED_DB=false), skipping")
        return

    db: Session = SessionLocal()
    try:
        if db.query(Product).count() > 0:
            logger.info("Database already seeded, skipping")
            return

        capabilities = load_capabilities()

        for spec in SAMPLE_PRODUCTS:
            product = Product(
                name=spec["name"], product_type=spec["product_type"],
                url=spec.get("url"), description=spec.get("description"),
                is_assessed=False, is_assessable=True,
            )
            db.add(product)
            db.flush()

            for key, value in spec["tags"]:
                db.add(Tag(key=key, value=value, product_id=product.id))

            for i, base_level in enumerate(spec["assessments"]):
                if i > 0:
                    # Mark previous score as not latest and flush before inserting new one
                    prev = db.query(Score).filter(Score.product_id == product.id, Score.latest.is_(True)).first()
                    if prev:
                        prev.latest = False
                        db.flush()

                _create_score(db, product, capabilities, base_level=base_level)
                db.flush()

            product.is_assessed = True

        db.commit()
        logger.info("Seeded database with %d example products", len(SAMPLE_PRODUCTS))
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
