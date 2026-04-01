import logging

from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Product, Score
from app.models.score import ALL_CAPABILITY_FIELDS
from app.capabilities import load_capabilities, load_formatted_capabilities, CATEGORIES
from app.config import settings
from app.queries import get_active_product, get_org_summary

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/products/{product_id}/scores")


@router.get("/")
async def index(request: Request, product_id: int, db: Session = Depends(get_db)):
    product = get_active_product(db, product_id)
    if not product:
        return RedirectResponse(url="/products", status_code=303)

    scores = (
        db.query(Score)
        .filter(Score.product_id == product_id)
        .order_by(Score.created_at.desc())
        .all()
    )

    capabilities = load_capabilities()

    # Build chart data (chronological order for the chart)
    scores_chrono = list(reversed(scores))
    history_labels = [s.created_at.strftime("%b %d, %Y") for s in scores_chrono]
    history_total = [round(float(s.total or 0), 2) for s in scores_chrono]
    history_cats = {
        cat["key"]: [round(float(getattr(s, cat["key"], 0) or 0), 2) for s in scores_chrono]
        for cat in CATEGORIES
    }

    return request.app.state.templates.TemplateResponse(
        request,
        "scores/index.html",
        context={
            "product": product,
            "scores": scores,
            "categories": CATEGORIES,
            "capabilities": capabilities,
            "config": settings,
            "history_labels": history_labels,
            "history_total": history_total,
            "history_cats": history_cats,
        },
    )


@router.get("/new")
async def new(request: Request, product_id: int, db: Session = Depends(get_db)):
    product = get_active_product(db, product_id, options=[
        selectinload(Product.scores.and_(Score.latest.is_(True))),
    ])
    if not product:
        return RedirectResponse(url="/products", status_code=303)

    capabilities = load_capabilities()
    formatted = load_formatted_capabilities()

    # Pre-populate from last score if exists
    prefill = {}
    if product.latest_score:
        for f in ALL_CAPABILITY_FIELDS:
            prefill[f] = getattr(product.latest_score, f, None)
        prefill["comment"] = product.latest_score.comment or ""

    return request.app.state.templates.TemplateResponse(
        request,
        "scores/new.html",
        context={
            "product": product,
            "capabilities": capabilities,
            "formatted_capabilities": formatted,
            "categories": CATEGORIES,
            "prefill": prefill,
            "config": settings,
        },
    )


@router.post("/")
async def create(request: Request, product_id: int, db: Session = Depends(get_db)):
    product = get_active_product(db, product_id)
    if not product or not product.is_assessable:
        return RedirectResponse(url="/products", status_code=303)

    form_data = await request.form()
    capabilities = load_capabilities()

    score = Score(product_id=product_id)

    for f in ALL_CAPABILITY_FIELDS:
        val = form_data.get(f)
        if val and val.isdigit() and 1 <= int(val) <= 4:
            setattr(score, f, int(val))

    score.comment = (form_data.get("comment", "") or "")[:4000]

    score.compute_totals(capabilities)

    # Archive previous latest scores before inserting new one
    if product.is_assessed:
        db.query(Score).filter(
            Score.product_id == product_id, Score.latest.is_(True)
        ).update({"latest": False}, synchronize_session=False)
        db.flush()
    else:
        product.is_assessed = True

    db.add(score)
    db.commit()
    logger.info("score_created product_id=%d score_id=%d total=%s", product_id, score.id, score.total)

    return RedirectResponse(url=f"/products/{product_id}?msg=score_saved", status_code=303)


@router.get("/{score_id}")
async def show(
    request: Request, product_id: int, score_id: int, db: Session = Depends(get_db)
):
    product = get_active_product(db, product_id)
    if not product:
        return RedirectResponse(url="/products", status_code=303)

    score = db.query(Score).filter(Score.id == score_id, Score.product_id == product_id).first()
    if not score:
        return RedirectResponse(url=f"/products/{product_id}", status_code=303)

    capabilities = load_capabilities()
    formatted = load_formatted_capabilities()

    # Build description arrays for each capability at its current score + next level
    descriptions = {}
    for f in ALL_CAPABILITY_FIELDS:
        val = getattr(score, f, None)
        if val is not None:
            desc_key = f"{f}_{val}"
            next_key = f"{f}_{val + 1}"
            next_desc = ""
            if val < 4:
                next_desc = capabilities.get(next_key, "")
            else:
                next_desc = "Woohoo !! You are already awesome here"
            descriptions[f] = {
                "score": val,
                "description": capabilities.get(desc_key, ""),
                "formatted": formatted.get(desc_key, ""),
                "next_description": next_desc,
            }
        else:
            descriptions[f] = {
                "score": 0, "description": "", "formatted": "", "next_description": ""
            }

    # Compute org-wide summary for comparison lines
    summary = get_org_summary(db)

    # Precompute JS arrays (avoids nested loop.parent in Jinja2)
    cap_labels = []
    cap_scores = []
    cat_expanded = []
    org_cap_scores = []
    org_cat_scores = []
    for cat in CATEGORIES:
        for field in cat["fields"]:
            cap_labels.append(capabilities.get(field, field))
            cap_scores.append(int(getattr(score, field, 0) or 0))
            cat_expanded.append(round(float(getattr(score, cat["key"], 0) or 0), 2))
            org_cap_scores.append(round(float(getattr(summary, field, 0) or 0), 2))
        org_cat_scores.append(round(float(getattr(summary, cat["key"], 0) or 0), 2))

    cat_labels = [capabilities.get(cat["key"], cat["key"]) for cat in CATEGORIES]
    cat_scores = [round(float(getattr(score, cat["key"], 0) or 0), 2) for cat in CATEGORIES]

    return request.app.state.templates.TemplateResponse(
        request,
        "scores/show.html",
        context={
            "product": product,
            "score": score,
            "categories": CATEGORIES,
            "capabilities": capabilities,
            "descriptions": descriptions,
            "cap_labels_json": cap_labels,
            "cap_scores_json": cap_scores,
            "cat_expanded_json": cat_expanded,
            "cat_labels_json": cat_labels,
            "cat_scores_json": cat_scores,
            "org_cap_scores_json": org_cap_scores,
            "org_cat_scores_json": org_cat_scores,
            "config": settings,
        },
    )
