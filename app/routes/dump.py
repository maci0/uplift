from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Product, Score
from app.models.score import ALL_CAPABILITY_FIELDS

router = APIRouter()


@router.get("/dump")
async def dump(db: Session = Depends(get_db)):
    products = (
        db.query(Product)
        .filter(Product.is_active.is_(True), Product.is_assessed.is_(True))
        .options(
            selectinload(Product.tags),
            selectinload(Product.scores.and_(Score.latest.is_(True))),
        )
        .all()
    )

    result = []
    for product in products:
        latest = product.latest_score
        if not latest:
            continue

        product_info = {
            "name": product.name,
            "type": product.product_type,
            "tags": {tag.key: tag.value for tag in product.tags},
        }

        categories = {
            "A": latest.a,
            "B": latest.b,
            "C": latest.c,
            "D": latest.d,
            "E": latest.e,
        }

        capabilities = {}
        for f in ALL_CAPABILITY_FIELDS:
            capabilities[f] = getattr(latest, f, None)

        result.append(
            {
                "productInfo": product_info,
                "categories": categories,
                "capabilities": capabilities,
                "cloudScore": latest.total,
            }
        )

    return result
