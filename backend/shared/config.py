"""
Centralized configuration management with environment variable validation using Pydantic.
"""
import os
from typing import Optional, Dict, Any, List
from pydantic import Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

logger = logging.getLogger(__name__)


class DatabaseConfig(BaseSettings):
    """Database configuration."""
    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    name: str = Field(default="demand_letters")
    user: str = Field(default="dev_user")
    password: str = Field(default="dev_password")
    
    @property
    def url(self) -> str:
        """Get database connection URL."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    model_config = SettingsConfigDict(
        env_prefix="DB_",
        case_sensitive=False,
    )


class AWSConfig(BaseSettings):
    """AWS configuration."""
    access_key_id: Optional[str] = Field(default=None)
    secret_access_key: Optional[str] = Field(default=None)
    region: str = Field(default="us-east-2")
    s3_bucket_documents: str
    s3_bucket_exports: str
    
    @field_validator("s3_bucket_documents", "s3_bucket_exports")
    @classmethod
    def validate_bucket_names(cls, v):
        """Validate S3 bucket names are not empty."""
        if not v or not v.strip():
            raise ValueError("S3 bucket name cannot be empty")
        return v.strip()
    
    model_config = SettingsConfigDict(
        case_sensitive=False,
        # Use custom source to read AWS_S3_BUCKET_* variables
        env_prefix="AWS_",
        # Override env var names for S3 buckets
        env_nested_delimiter="__",
    )
    
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        """Customize settings sources to map AWS_S3_BUCKET_* env vars."""
        import os
        
        def custom_env_source() -> Dict[str, Any]:
            """Map AWS_* environment variables to field names."""
            result = {}
            # Read all AWS_ prefixed vars
            for key, value in os.environ.items():
                if key.startswith("AWS_"):
                    # Convert AWS_ACCESS_KEY_ID -> access_key_id
                    # Convert AWS_S3_BUCKET_DOCUMENTS -> s3_bucket_documents
                    field_name = key[4:].lower()  # Remove AWS_ prefix and lowercase
                    result[field_name] = value
            return result
        
        # Use custom source before dotenv (so .env file can override)
        return (
            init_settings,
            custom_env_source,
            dotenv_settings,
            file_secret_settings,
        )


class OpenAIConfig(BaseSettings):
    """OpenAI configuration."""
    api_key: str = Field(...)
    model: str = Field(default="gpt-4")
    temperature: float = Field(default=0.7)
    
    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v):
        """Validate temperature is between 0 and 2."""
        if not 0 <= v <= 2:
            raise ValueError("Temperature must be between 0 and 2")
        return v
    
    model_config = SettingsConfigDict(
        env_prefix="OPENAI_",
        case_sensitive=False,
    )


class CORSConfig(BaseSettings):
    """CORS configuration."""
    allow_origins: List[str] = Field(
        default=["*"],
        description="List of allowed CORS origins. Use '*' for all origins."
    )
    allow_credentials: bool = Field(
        default=True,
        description="Whether to allow credentials in CORS requests."
    )
    allow_methods: List[str] = Field(
        default=["*"],
        description="List of allowed HTTP methods. Use '*' for all methods."
    )
    allow_headers: List[str] = Field(
        default=["*"],
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
    
    model_config = SettingsConfigDict(
        env_prefix="CORS_",
        case_sensitive=False,
    )


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
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        arbitrary_types_allowed=True,
        extra="ignore",  # Ignore extra fields - they're handled by nested configs
    )


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
