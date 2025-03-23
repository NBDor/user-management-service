from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, PostgresDsn, field_validator, ValidationInfo
from typing import List, Optional, Any, Union


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "YOUR_SECRET_KEY_HERE"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SERVER_NAME: Optional[str] = None
    SERVER_HOST: Optional[AnyHttpUrl] = None
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    PROJECT_NAME: str = "User Management Service"

    POSTGRES_SERVER: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    POSTGRES_PORT: Optional[str] = "5432"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    TEST_POSTGRES_SERVER: Optional[str] = None
    TEST_POSTGRES_USER: Optional[str] = None
    TEST_POSTGRES_PASSWORD: Optional[str] = None
    TEST_POSTGRES_DB: Optional[str] = None
    TEST_POSTGRES_PORT: Optional[str] = "5432"
    TEST_SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    FIRST_SUPERUSER: Optional[str] = None
    FIRST_SUPERUSER_PASSWORD: Optional[str] = None

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
            
        # Get data safely with fallback to None
        user = info.data.get("POSTGRES_USER")
        password = info.data.get("POSTGRES_PASSWORD")
        host = info.data.get("POSTGRES_SERVER") 
        db = info.data.get("POSTGRES_DB")
        
        # Only build if we have all required components
        if not (user and password and host and db):
            return None
            
        return PostgresDsn.build(
            scheme="postgresql",
            username=user,
            password=password,
            host=host,
            path=f"/{db}",
        )

    @field_validator("TEST_SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_test_db_connection(cls, v: Optional[str], info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
            
        # Get data safely with fallback to None
        user = info.data.get("TEST_POSTGRES_USER")
        password = info.data.get("TEST_POSTGRES_PASSWORD")
        host = info.data.get("TEST_POSTGRES_SERVER")
        db = info.data.get("TEST_POSTGRES_DB")
        
        # Only build if we have all required components
        if not (user and password and host and db):
            return None
            
        return PostgresDsn.build(
            scheme="postgresql",
            username=user,
            password=password,
            host=host,
            path=f"/{db}",
        )

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")


settings = Settings()