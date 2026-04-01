import logging

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Tag
from app.config import settings
from app.logging_config import sanitize_log
from app.queries import get_active_product, get_tag

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/products/{product_id}/tags")


@router.get("/new")
async def new(request: Request, product_id: int, db: Session = Depends(get_db)):
    product = get_active_product(db, product_id)
    if not product:
        return RedirectResponse(url="/products", status_code=303)

    return request.app.state.templates.TemplateResponse(
        request,
        "tags/new.html",
        context={"product": product, "config": settings},
    )


@router.post("/")
async def create(
    request: Request,
    product_id: int,
    key: str = Form(...),
    value: str = Form(...),
    db: Session = Depends(get_db),
):
    product = get_active_product(db, product_id)
    if not product:
        return RedirectResponse(url="/products", status_code=303)

    key, value = key.strip(), value.strip()
    if not key or not value or len(key) > 255 or len(value) > 255:
        return RedirectResponse(url=f"/products/{product_id}/tags/new", status_code=303)

    tag = Tag(key=key, value=value, product_id=product_id)
    db.add(tag)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        logger.warning("tag_duplicate product_id=%d key=%s", product_id, sanitize_log(key))
        return RedirectResponse(
            url=f"/products/{product_id}?msg=tag_duplicate", status_code=303
        )
    logger.info("tag_created product_id=%d key=%s", product_id, sanitize_log(key))
    return RedirectResponse(url=f"/products/{product_id}?msg=tag_added", status_code=303)


@router.get("/{tag_id}/edit")
async def edit(
    request: Request, product_id: int, tag_id: int, db: Session = Depends(get_db)
):
    if not settings.enable_tag_modification:
        return RedirectResponse(url=f"/products/{product_id}", status_code=303)

    product = get_active_product(db, product_id)
    tag = get_tag(db, tag_id, product_id)
    if not product or not tag:
        return RedirectResponse(url=f"/products/{product_id}", status_code=303)

    return request.app.state.templates.TemplateResponse(
        request,
        "tags/edit.html",
        context={"product": product, "tag": tag, "config": settings},
    )


@router.post("/{tag_id}")
async def update(
    request: Request,
    product_id: int,
    tag_id: int,
    key: str = Form(...),
    value: str = Form(...),
    db: Session = Depends(get_db),
):
    if not settings.enable_tag_modification:
        return RedirectResponse(url=f"/products/{product_id}", status_code=303)

    product = get_active_product(db, product_id)
    if not product:
        return RedirectResponse(url="/products", status_code=303)

    key, value = key.strip(), value.strip()
    if not key or not value or len(key) > 255 or len(value) > 255:
        return RedirectResponse(url=f"/products/{product_id}/tags/{tag_id}/edit", status_code=303)

    tag = get_tag(db, tag_id, product_id)
    if tag:
        tag.key = key
        tag.value = value
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            logger.warning("tag_duplicate product_id=%d key=%s", product_id, sanitize_log(key))
            return RedirectResponse(
                url=f"/products/{product_id}?msg=tag_duplicate", status_code=303
            )
        logger.info("tag_updated id=%d product_id=%d key=%s", tag_id, product_id, sanitize_log(key))
    else:
        logger.warning("tag_update_not_found id=%d product_id=%d", tag_id, product_id)
        return RedirectResponse(url=f"/products/{product_id}", status_code=303)
    return RedirectResponse(url=f"/products/{product_id}?msg=tag_updated", status_code=303)


@router.post("/{tag_id}/delete")
async def destroy(product_id: int, tag_id: int, db: Session = Depends(get_db)):
    if not settings.enable_tag_modification:
        return RedirectResponse(url=f"/products/{product_id}", status_code=303)

    product = get_active_product(db, product_id)
    if not product:
        return RedirectResponse(url="/products", status_code=303)

    tag = get_tag(db, tag_id, product_id)
    if tag:
        db.delete(tag)
        db.commit()
        logger.info("tag_deleted id=%d product_id=%d", tag_id, product_id)
    else:
        logger.warning("tag_delete_not_found id=%d product_id=%d", tag_id, product_id)
    return RedirectResponse(url=f"/products/{product_id}?msg=tag_deleted", status_code=303)
