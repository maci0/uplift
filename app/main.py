from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.config import VERSION
from app.csrf import CSRFMiddleware
from app.database import engine
from app.logging_config import setup_logging, log_startup_config
from app.middleware import RequestLoggingMiddleware
from app.models.base import Base
from app.routes import dashboard, products, scores, tags, pages, dump
from app.routes import health

# Configure logging before anything else
setup_logging()

BASE_DIR = Path(__file__).parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    engine.dispose()


app = FastAPI(title="Uplift", version=VERSION, docs_url=None, redoc_url=None, lifespan=lifespan)

# Middleware (outermost first)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(CSRFMiddleware)

# Static files
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Templates
templates = Jinja2Templates(directory=BASE_DIR / "templates")
templates.env.globals["VERSION"] = VERSION
app.state.templates = templates

# Create tables and seed
Base.metadata.create_all(bind=engine)
from app.seed import seed_db
seed_db()

# Register routers
app.include_router(health.router)
app.include_router(dashboard.router)
app.include_router(products.router)
app.include_router(scores.router)
app.include_router(tags.router)
app.include_router(pages.router)
app.include_router(dump.router)

# Log startup config
log_startup_config()
