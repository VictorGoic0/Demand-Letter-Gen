"""
Centralized configuration management with environment variable validation using Pydantic.
"""
import os
from typing import Optional, Dict, Any, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
import logging

logger = logging.getLogger(__name__)


class DatabaseConfig(BaseSettings):
    """Database configuration."""
    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=5432, env="DB_PORT")
    name: str = Field(default="demand_letters", env="DB_NAME")
    user: str = Field(default="dev_user", env="DB_USER")
    password: str = Field(default="dev_password", env="DB_PASSWORD")
    
    @property
    def url(self) -> str:
        """Get database connection URL."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    class Config:
        env_prefix = "DB_"
        case_sensitive = False


class AWSConfig(BaseSettings):
    """AWS configuration."""
    access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    region: str = Field(default="us-east-2", env="AWS_REGION")
    s3_bucket_documents: str = Field(..., env="S3_BUCKET_DOCUMENTS")
    s3_bucket_exports: str = Field(..., env="S3_BUCKET_EXPORTS")
    
    @field_validator("s3_bucket_documents", "s3_bucket_exports")
    @classmethod
    def validate_bucket_names(cls, v):
        """Validate S3 bucket names are not empty."""
        if not v or not v.strip():
            raise ValueError("S3 bucket name cannot be empty")
        return v.strip()
    
    class Config:
        env_prefix = "AWS_"
        case_sensitive = False


class OpenAIConfig(BaseSettings):
    """OpenAI configuration."""
    api_key: str = Field(..., env="OPENAI_API_KEY")
    model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    max_tokens: int = Field(default=2000, env="OPENAI_MAX_TOKENS")
    
    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v):
        """Validate temperature is between 0 and 2."""
        if not 0 <= v <= 2:
            raise ValueError("Temperature must be between 0 and 2")
        return v
    
    @field_validator("max_tokens")
    @classmethod
    def validate_max_tokens(cls, v):
        """Validate max_tokens is positive."""
        if v < 1:
            raise ValueError("max_tokens must be at least 1")
        return v
    
    class Config:
        env_prefix = "OPENAI_"
        case_sensitive = False


class CORSConfig(BaseSettings):
    """CORS configuration."""
    allow_origins: List[str] = Field(
        default=["*"],
        env="CORS_ALLOW_ORIGINS",
        description="List of allowed CORS origins. Use '*' for all origins."
    )
    allow_credentials: bool = Field(
        default=True,
        env="CORS_ALLOW_CREDENTIALS",
        description="Whether to allow credentials in CORS requests."
    )
    allow_methods: List[str] = Field(
        default=["*"],
        env="CORS_ALLOW_METHODS",
        description="List of allowed HTTP methods. Use '*' for all methods."
    )
    allow_headers: List[str] = Field(
        default=["*"],
        env="CORS_ALLOW_HEADERS",
        description="List of allowed headers. Use '*' for all headers."
    )
    
    @field_validator("allow_origins", mode="before")
    @classmethod
    def parse_origins(cls, v):
        """Parse comma-separated origins string or return list."""
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    @field_validator("allow_methods", mode="before")
    @classmethod
    def parse_methods(cls, v):
        """Parse comma-separated methods string or return list."""
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [method.strip().upper() for method in v.split(",") if method.strip()]
        return v
    
    @field_validator("allow_headers", mode="before")
    @classmethod
    def parse_headers(cls, v):
        """Parse comma-separated headers string or return list."""
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [header.strip() for header in v.split(",") if header.strip()]
        return v
    
    class Config:
        env_prefix = "CORS_"
        case_sensitive = False


class Settings(BaseSettings):
    """Application settings with all configuration."""
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Note: Nested BaseSettings models are instantiated in __init__
    database: Optional[DatabaseConfig] = None
    aws: Optional[AWSConfig] = None
    openai: Optional[OpenAIConfig] = None
    cors: Optional[CORSConfig] = None
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        """Validate environment is one of the allowed values."""
        valid_environments = ["development", "staging", "production"]
        if v.lower() not in valid_environments:
            raise ValueError(
                f"Invalid environment: {v}. Must be one of: {', '.join(valid_environments)}"
            )
        return v.lower()
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level is one of the allowed values."""
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_log_levels:
            raise ValueError(
                f"Invalid log level: {v}. Must be one of: {', '.join(valid_log_levels)}"
            )
        return v.upper()
    
    def __init__(self, **kwargs):
        """Initialize Settings and load nested configurations."""
        super().__init__(**kwargs)
        # Load nested BaseSettings models
        if self.database is None:
            self.database = DatabaseConfig()
        if self.aws is None:
            self.aws = AWSConfig()
        if self.openai is None:
            self.openai = OpenAIConfig()
        if self.cors is None:
            self.cors = CORSConfig()
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        # Allow nested models to be instantiated
        arbitrary_types_allowed = True


class ConfigError(Exception):
    """Raised when configuration is invalid or missing required values."""
    pass


# Global settings instance
_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get or create the global settings instance (singleton).
    
    Returns:
        Settings instance
        
    Raises:
        ConfigError: If settings cannot be loaded
    """
    global _settings_instance
    if _settings_instance is None:
        try:
            _settings_instance = Settings()
            logger.info(f"Settings loaded successfully for environment: {_settings_instance.environment}")
        except Exception as e:
            logger.error(f"Failed to load settings: {str(e)}")
            raise ConfigError(f"Failed to load settings: {str(e)}")
    return _settings_instance


def reload_settings() -> Settings:
    """
    Reload settings from environment variables.
    Useful for testing or when environment changes.
    
    Returns:
        New Settings instance
    """
    global _settings_instance
    _settings_instance = None
    return get_settings()


def get_config_summary(settings: Settings) -> Dict[str, Any]:
    """
    Get a summary of the settings (safe for logging, excludes secrets).
    
    Args:
        settings: Settings instance
        
    Returns:
        Dictionary with settings summary
    """
    return {
        "environment": settings.environment,
        "debug": settings.debug,
        "log_level": settings.log_level,
        "database": {
            "host": settings.database.host,
            "port": settings.database.port,
            "name": settings.database.name,
            "user": settings.database.user,
        },
        "aws": {
            "region": settings.aws.region,
            "s3_bucket_documents": settings.aws.s3_bucket_documents,
            "s3_bucket_exports": settings.aws.s3_bucket_exports,
            "credentials_configured": bool(settings.aws.access_key_id and settings.aws.secret_access_key),
        },
        "openai": {
            "model": settings.openai.model,
            "temperature": settings.openai.temperature,
            "max_tokens": settings.openai.max_tokens,
            "api_key_configured": bool(settings.openai.api_key),
        },
        "cors": {
            "allow_origins": settings.cors.allow_origins,
            "allow_credentials": settings.cors.allow_credentials,
            "allow_methods": settings.cors.allow_methods,
            "allow_headers": settings.cors.allow_headers,
        },
    }


# Backward compatibility aliases
def get_config() -> Settings:
    """Alias for get_settings() for backward compatibility."""
    return get_settings()


def load_config() -> Settings:
    """Alias for get_settings() for backward compatibility."""
    return get_settings()
