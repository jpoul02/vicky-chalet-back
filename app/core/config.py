from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    INTERNAL_API_KEY: str = ""
    AUTH_PIN: str = ""
    COOKIE_SECURE: bool = False  # Set to True in production (HTTPS)

    model_config = {"env_file": ".env"}

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            # Accept comma-separated: "http://a.com,http://b.com"
            # or JSON array: '["http://a.com"]'
            v = v.strip()
            if v.startswith("["):
                import json
                return json.loads(v)
            return [o.strip() for o in v.split(",") if o.strip()]
        return v


settings = Settings()
