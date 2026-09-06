"""
Centralized application settings, loaded from environment variables.
Equivalent to appsettings.json + IOptions<T> pattern in .NET.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Firebase
    firebase_service_account_path: str = "firebase-service-account.json"

    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_bucket: str = "qr-images"

    # Google Safe Browsing
    google_safe_browsing_key: str

        # Gemini AI Assistant
    gemini_api_key: str

    # App
    environment: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = False
        # Admin panel

settings = Settings()