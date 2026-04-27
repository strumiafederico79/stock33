from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    app_name: str = "Stock Control Pro Enterprise V2"
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:////data/stock_control.db"
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 720
    default_admin_username: str = "admin"
    default_admin_password: str = "admin1234"
    default_admin_full_name: str = "Administrador General"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://3.88.51.188,http://3.88.51.188:80"
    public_base_url: str = "http://3.88.51.188"
    company_name: str = "Stock Control Pro"
@lru_cache
def get_settings():
    return Settings()
