from importlib.metadata import version, PackageNotFoundError

from pydantic_settings import BaseSettings

try:
    VERSION = version("uplift")
except PackageNotFoundError:
    VERSION = "dev"


class Settings(BaseSettings):
    database_url: str = "sqlite:///./uplift.db"
    enable_asset_creation: bool = True
    enable_tag_modification: bool = True
    seed_db: bool = True
    slack_endpoint: str = ""
    slack_channel: str = ""

    model_config = {"env_prefix": "UPLIFT_"}


settings = Settings()
