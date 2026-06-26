from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Aplicación
    APP_NAME: str = "Sistema Óptica"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # MongoDB
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "optica_clinico"
    
    # Redis
    REDIS_URL: str
    REDIS_CACHE_TTL: int = 3600
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = "Sistema Óptica"
    
    # CFDI
    CFDI_PROVIDER: str = "MOCK"
    CFDI_API_URL: str = ""
    CFDI_API_KEY: str = ""
    CFDI_TIMEOUT_SECONDS: float = 10.0
    CFDI_CERTIFICATE_PATH: str = ""
    CFDI_KEY_PATH: str = ""
    CFDI_PASSWORD_CERT: str = ""
    
    # Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10485760
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()