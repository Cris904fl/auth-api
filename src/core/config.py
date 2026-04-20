# flake8: noqa: E402
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Auth API"
    app_version: str = "1.0.0"
    debug: bool = False

    # JWT
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Google OAuth2
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"

    # AWS DynamoDB
    aws_region: str = "us-east-1"
    aws_access_key_id: str = "local"
    aws_secret_access_key: str = "local"
    dynamodb_endpoint_url: str = ""
    users_table: str = "users"

    class Config:
        env_file = ".env"


settings = Settings()
