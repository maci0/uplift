from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.capabilities import load_capabilities, CATEGORIES
from app.config import settings

router = APIRouter()


@router.get("/github")
async def github_redirect():
    return RedirectResponse(url="https://github.com/techmaturity/techmaturity")  # TODO: update when repo is renamed


@router.get("/docs")
async def docs(request: Request):
    capabilities = load_capabilities()
    return request.app.state.templates.TemplateResponse(
        request,
        "pages/docs.html",
        context={
            "categories": CATEGORIES,
            "capabilities": capabilities,
            "config": settings,
        },
    )


@router.get("/about")
async def about(request: Request):
    return request.app.state.templates.TemplateResponse(
        request,
        "pages/about.html",
        context={"config": settings},
    )
