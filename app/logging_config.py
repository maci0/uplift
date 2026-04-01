import logging
import sys
from app.config import settings, VERSION


def sanitize_log(value: str) -> str:
    """Strip newlines to prevent log injection."""
    return value.replace("\n", "\\n").replace("\r", "\\r")


def setup_logging() -> None:
    """Configure logging for the application."""
    log_format = (
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
        force=True,
    )
    # Quiet noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def log_startup_config() -> None:
    """Log application configuration at startup (redacting secrets)."""
    logger = logging.getLogger("app.startup")
    db_url = settings.database_url
    if "://" in db_url:
        # Redact credentials from database URL
        scheme, rest = db_url.split("://", 1)
        if "@" in rest:
            rest = rest.split("@", 1)[1]
            db_url = f"{scheme}://***@{rest}"

    logger.info("Uplift v%s starting", VERSION)
    logger.info("database=%s", db_url)
    logger.info(
        "features: asset_creation=%s tag_modification=%s",
        settings.enable_asset_creation,
        settings.enable_tag_modification,
    )
    logger.info("slack_configured=%s", bool(settings.slack_endpoint))
