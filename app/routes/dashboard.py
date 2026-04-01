from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Product, Score
from app.capabilities import load_capabilities, CATEGORIES, get_capability_labels
from app.config import settings
from app.queries import get_org_summary

router = APIRouter()


@router.get("/")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    # First-time visitor detection
    first_visit = False
    if settings.enable_first_time_user_exp and not request.cookies.get("first_visit"):
        first_visit = True

    capabilities = load_capabilities()

    # Get summary: average of all latest scores
    summary = get_org_summary(db)

    # Product count
    product_count = db.query(func.count(Product.id)).filter(
        Product.is_active.is_(True), Product.is_assessed.is_(True)
    ).scalar()

    # Build summary data for template
    summary_data = {}
    if summary and summary.total is not None:
        summary_data["total"] = float(round(summary.total, 2))
        for cat in CATEGORIES:
            cat_val = getattr(summary, cat["key"], 0) or 0
            summary_data[cat["key"]] = float(round(cat_val, 2))
            for field in cat["fields"]:
                val = getattr(summary, field, 0) or 0
                summary_data[field] = float(round(val, 2))
    else:
        summary_data["total"] = 0
        for cat in CATEGORIES:
            summary_data[cat["key"]] = 0
            for field in cat["fields"]:
                summary_data[field] = 0

    capability_labels = get_capability_labels(capabilities)

    # Precompute arrays for JS (avoids nested loop.parent in Jinja2)
    cap_scores = []
    cap_fields = []
    cat_expanded = []
    for cat in CATEGORIES:
        for field in cat["fields"]:
            cap_scores.append(summary_data[field])
            cap_fields.append(field)
            cat_expanded.append(summary_data[cat["key"]])

    # Build capability details for click modal
    cap_details = {}
    for field in cap_fields:
        cap_details[field] = {
            "name": capabilities.get(field, field),
            "levels": [
                capabilities.get(f"{field}_1", ""),
                capabilities.get(f"{field}_2", ""),
                capabilities.get(f"{field}_3", ""),
                capabilities.get(f"{field}_4", ""),
            ],
            "min": capabilities.get(f"{field}_min"),
        }

    # Build recommendations
    recommendations = []
    if product_count and product_count > 0:
        # 1. Capabilities below their minimum threshold
        below_min = []
        for field in cap_fields:
            min_val = capabilities.get(f"{field}_min")
            if min_val is not None:
                score = summary_data.get(field, 0)
                if score < min_val:
                    below_min.append({
                        "name": capabilities.get(field, field),
                        "score": round(score, 1),
                        "min": min_val,
                        "gap": round(min_val - score, 1),
                    })
        below_min.sort(key=lambda x: x["gap"], reverse=True)
        for item in below_min[:5]:
            recommendations.append({
                "type": "critical",
                "title": item["name"],
                "text": f"Org average {item['score']} is below the cloud-readiness minimum of {item['min']}. Close the gap of {item['gap']} to improve cloud readiness.",
            })

        # 2. Weakest category
        cat_scores = [(cat["key"], capabilities.get(cat["key"], cat["key"]), summary_data.get(cat["key"], 0)) for cat in CATEGORIES]
        cat_scores.sort(key=lambda x: x[2])
        if cat_scores and cat_scores[0][2] < 3:
            weakest = cat_scores[0]
            recommendations.append({
                "type": "improve",
                "title": f"Weakest category: {weakest[1]}",
                "text": f"Organization average is {round(weakest[2], 1)}/4. Focus investment here for the biggest overall improvement.",
            })

        # 3. Lowest-scoring capabilities (not already covered by below_min)
        below_min_names = {item["name"] for item in below_min}
        low_caps = []
        for field in cap_fields:
            name = capabilities.get(field, field)
            if name not in below_min_names:
                low_caps.append({"name": name, "score": summary_data.get(field, 0)})
        low_caps.sort(key=lambda x: x["score"])
        for item in low_caps[:3]:
            if item["score"] < 2.5:
                recommendations.append({
                    "type": "improve",
                    "title": item["name"],
                    "text": f"Org average is {round(item['score'], 1)}/4. Consider targeted improvement initiatives.",
                })

        # 4. Strengths
        high_caps = sorted(
            [{"name": capabilities.get(f, f), "score": summary_data.get(f, 0)} for f in cap_fields],
            key=lambda x: x["score"], reverse=True,
        )
        for item in high_caps[:2]:
            if item["score"] >= 3:
                recommendations.append({
                    "type": "strength",
                    "title": item["name"],
                    "text": f"Org average is {round(item['score'], 1)}/4. This is a strong capability across the organization.",
                })

    response = request.app.state.templates.TemplateResponse(
        request,
        "pages/dashboard.html",
        context={
            "summary": summary_data,
            "product_count": product_count or 0,
            "categories": CATEGORIES,
            "capabilities": capabilities,
            "capability_labels": capability_labels,
            "cap_scores_json": cap_scores,
            "cap_fields_json": cap_fields,
            "cap_details_json": cap_details,
            "cat_expanded_json": cat_expanded,
            "recommendations": recommendations,
            "first_visit": first_visit,
            "config": settings,
        },
    )

    if first_visit:
        response.set_cookie(
            key="first_visit", value="1", max_age=365 * 24 * 3600,
            httponly=True, samesite="lax",
        )

    return response


@router.get("/org-history")
async def org_history(request: Request, db: Session = Depends(get_db)):
    """Show organization cloud readiness score over time."""
    capabilities = load_capabilities()

    # Get all scores ordered chronologically, joined with active products
    all_scores = (
        db.query(Score)
        .join(Product)
        .filter(Product.is_active.is_(True))
        .order_by(Score.created_at.asc())
        .all()
    )

    # Reconstruct org average at each point in time
    # Maintain a running dict of product_id -> score data
    product_latest = {}  # product_id -> {total, a, b, c, d, e}
    timeline = []

    for score in all_scores:
        product_latest[score.product_id] = {
            "total": score.total or 0,
            "a": score.a or 0,
            "b": score.b or 0,
            "c": score.c or 0,
            "d": score.d or 0,
            "e": score.e or 0,
        }

        # Compute org averages at this point
        n = len(product_latest)
        avg_total = sum(v["total"] for v in product_latest.values()) / n
        avg_cats = {}
        for key in ["a", "b", "c", "d", "e"]:
            avg_cats[key] = round(sum(v[key] for v in product_latest.values()) / n, 2)

        timeline.append({
            "date": score.created_at.strftime("%b %d, %Y"),
            "total": round(avg_total, 2),
            "products": n,
            **avg_cats,
        })

    history_labels = [p["date"] for p in timeline]
    history_total = [p["total"] for p in timeline]
    history_products = [p["products"] for p in timeline]
    history_cats = {key: [p[key] for p in timeline] for key in ["a", "b", "c", "d", "e"]}

    cat_labels = [capabilities.get(cat["key"], cat["key"]) for cat in CATEGORIES]

    return request.app.state.templates.TemplateResponse(
        request,
        "pages/org_history.html",
        context={
            "history_labels": history_labels,
            "history_total": history_total,
            "history_products": history_products,
            "history_cats": history_cats,
            "cat_labels": cat_labels,
            "timeline": timeline,
            "config": settings,
        },
    )
