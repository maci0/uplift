import logging

from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func, or_
from math import ceil

from app.database import get_db
from app.models import Product, Tag, Score
from app.capabilities import load_capabilities, CATEGORIES
from app.config import settings
from app.logging_config import sanitize_log
from app.queries import get_active_product, get_org_summary

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/products")

PER_PAGE = 10
VALID_PRODUCT_TYPES = {"Product", "Component", "Sub component", "Service", "Application"}


@router.get("/")
async def index(
    request: Request,
    q: str = "",
    assessed: str = "",
    page: int = Query(1, ge=1, le=10000),
    db: Session = Depends(get_db),
):
    query = db.query(Product).filter(Product.is_active.is_(True))
    query = query.options(
        selectinload(Product.tags),
        selectinload(Product.scores.and_(Score.latest.is_(True))),
    )

    if q:
        terms = q.split()
        # OR logic: match products having ANY tag value matching ANY term (same as Rails)
        or_conditions = []
        for term in terms:
            escaped = term.strip().lower().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            or_conditions.append(
                Product.tags.any(func.lower(Tag.value).like(f"%{escaped}%", escape="\\"))
            )
        query = query.filter(or_(*or_conditions))

    if assessed == "1":
        query = query.filter(Product.is_assessed.is_(True))

    query = query.order_by(Product.name)

    total = query.count()
    total_pages = ceil(total / PER_PAGE) if total > 0 else 1
    products = query.offset((page - 1) * PER_PAGE).limit(PER_PAGE).all()

    template_name = "products/index.html"

    # Check if this is an htmx request (partial update)
    if request.headers.get("HX-Request"):
        template_name = "products/_products.html"

    return request.app.state.templates.TemplateResponse(
        request,
        template_name,
        context={
            "products": products,
            "query": q,
            "assessed": assessed,
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "config": settings,
        },
    )


@router.get("/new")
async def new(request: Request):
    if not settings.enable_asset_creation:
        return RedirectResponse(url="/products", status_code=303)
    return request.app.state.templates.TemplateResponse(
        request,
        "products/new.html",
        context={"config": settings},
    )


@router.post("/")
async def create(
    request: Request,
    db: Session = Depends(get_db),
):
    if not settings.enable_asset_creation:
        return RedirectResponse(url="/products", status_code=303)

    form_data = await request.form()
    name = form_data.get("name", "").strip()
    product_type = form_data.get("product_type", "")
    url = form_data.get("url", "").strip() or None
    description = form_data.get("description", "").strip() or None

    if not name or product_type not in VALID_PRODUCT_TYPES:
        return RedirectResponse(url="/products/new", status_code=303)

    product = Product(name=name, product_type=product_type, url=url, description=description, is_assessed=False)
    db.add(product)
    db.flush()

    # Process tags (parallel arrays of tag_key / tag_value)
    tag_keys = form_data.getlist("tag_key")
    tag_values = form_data.getlist("tag_value")
    for key, value in zip(tag_keys, tag_values):
        key, value = key.strip(), value.strip()
        if key and value:
            db.add(Tag(key=key, value=value, product_id=product.id))

    db.commit()
    db.refresh(product)
    logger.info("product_created id=%d name=%s type=%s", product.id, sanitize_log(name), sanitize_log(product_type))
    return RedirectResponse(url=f"/products/{product.id}?msg=asset_created", status_code=303)


@router.get("/{product_id}")
async def show(request: Request, product_id: int, db: Session = Depends(get_db)):
    product = get_active_product(db, product_id, options=[
        selectinload(Product.tags),
        selectinload(Product.scores),
    ])
    if not product:
        return RedirectResponse(url="/products", status_code=303)

    # Build radar chart data if product has been assessed
    capabilities = load_capabilities()
    cat_labels = [capabilities.get(cat["key"], cat["key"]) for cat in CATEGORIES]
    cat_scores = []
    org_cat_scores = []
    if product.latest_score:
        cat_scores = [round(float(getattr(product.latest_score, cat["key"], 0) or 0), 2) for cat in CATEGORIES]
        summary = get_org_summary(db)
        if summary:
            org_cat_scores = [round(float(getattr(summary, cat["key"], 0) or 0), 2) for cat in CATEGORIES]

    return request.app.state.templates.TemplateResponse(
        request,
        "products/show.html",
        context={
            "product": product,
            "total_scores": len(product.scores),
            "cat_labels": cat_labels,
            "cat_scores": cat_scores,
            "org_cat_scores": org_cat_scores,
            "config": settings,
        },
    )


@router.get("/{product_id}/edit")
async def edit(request: Request, product_id: int, db: Session = Depends(get_db)):
    product = get_active_product(db, product_id)
    if not product:
        return RedirectResponse(url="/products", status_code=303)

    return request.app.state.templates.TemplateResponse(
        request,
        "products/edit.html",
        context={"product": product, "config": settings},
    )


@router.post("/{product_id}")
async def update(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
):
    product = get_active_product(db, product_id)
    if not product:
        return RedirectResponse(url="/products", status_code=303)

    form_data = await request.form()
    name = form_data.get("name", "").strip()
    product_type = form_data.get("product_type", "")
    url = form_data.get("url", "").strip() or None
    description = form_data.get("description", "").strip() or None

    if not name or product_type not in VALID_PRODUCT_TYPES:
        return RedirectResponse(url=f"/products/{product_id}/edit", status_code=303)

    product.name = name
    product.product_type = product_type
    product.url = url
    product.description = description
    db.commit()
    logger.info("product_updated id=%d name=%s type=%s", product_id, sanitize_log(name), sanitize_log(product_type))
    return RedirectResponse(url=f"/products/{product.id}?msg=asset_updated", status_code=303)


@router.post("/{product_id}/delete")
async def destroy(product_id: int, db: Session = Depends(get_db)):
    product = get_active_product(db, product_id)
    if product:
        product.is_active = False
        db.commit()
        logger.info("product_deleted id=%d", product_id)
    else:
        logger.warning("product_delete_not_found id=%d", product_id)
    return RedirectResponse(url="/products?msg=asset_deleted", status_code=303)
