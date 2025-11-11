"""
Centralized configuration management with environment variable validation.
"""
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str
    port: int
    name: str
    user: str
    password: str
    
    @property
    def url(self) -> str:
        """Get database connection URL."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass
class AWSConfig:
    """AWS configuration."""
    access_key_id: Optional[str]
    secret_access_key: Optional[str]
    region: str
    s3_bucket_documents: str
    s3_bucket_exports: str


@dataclass
class OpenAIConfig:
    """OpenAI configuration."""
    api_key: str
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000


@dataclass
class AppConfig:
    """Application configuration."""
    environment: str
    debug: bool
    log_level: str
    database: DatabaseConfig
    aws: AWSConfig
    openai: OpenAIConfig
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"


class ConfigError(Exception):
    """Raised when configuration is invalid or missing required values."""
    pass


def get_env_var(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    Get environment variable with validation.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        required: Whether the variable is required
        
    Returns:
        Environment variable value or default
        
    Raises:
        ConfigError: If required variable is missing
    """
    value = os.getenv(key, default)
    
    if required and not value:
        raise ConfigError(f"Required environment variable '{key}' is not set")
    
    return value


def get_env_int(key: str, default: int, required: bool = False) -> int:
    """
    Get integer environment variable.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        required: Whether the variable is required
        
    Returns:
        Integer value
        
    Raises:
        ConfigError: If value cannot be converted to int
    """
    value = get_env_var(key, str(default), required)
    try:
        return int(value)
    except (ValueError, TypeError) as e:
        raise ConfigError(f"Environment variable '{key}' must be an integer: {value}")


def get_env_float(key: str, default: float, required: bool = False) -> float:
    """
    Get float environment variable.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        required: Whether the variable is required
        
    Returns:
        Float value
        
    Raises:
        ConfigError: If value cannot be converted to float
    """
    value = get_env_var(key, str(default), required)
    try:
        return float(value)
    except (ValueError, TypeError) as e:
        raise ConfigError(f"Environment variable '{key}' must be a float: {value}")


def get_env_bool(key: str, default: bool = False, required: bool = False) -> bool:
    """
    Get boolean environment variable.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        required: Whether the variable is required
        
    Returns:
        Boolean value
        
    Raises:
        ConfigError: If value cannot be converted to bool
    """
    value = get_env_var(key, str(default), required)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on")
    return bool(value)


def load_database_config() -> DatabaseConfig:
    """
    Load database configuration from environment variables.
    
    Returns:
        DatabaseConfig instance
        
    Raises:
        ConfigError: If required variables are missing
    """
    return DatabaseConfig(
        host=get_env_var("DB_HOST", "localhost", required=False),
        port=get_env_int("DB_PORT", 5432, required=False),
        name=get_env_var("DB_NAME", "demand_letters", required=False),
        user=get_env_var("DB_USER", "dev_user", required=False),
        password=get_env_var("DB_PASSWORD", "dev_password", required=False),
    )


def load_aws_config() -> AWSConfig:
    """
    Load AWS configuration from environment variables.
    
    Returns:
        AWSConfig instance
        
    Raises:
        ConfigError: If required variables are missing
    """
    # AWS credentials can be optional if using IAM roles
    access_key_id = get_env_var("AWS_ACCESS_KEY_ID", required=False)
    secret_access_key = get_env_var("AWS_SECRET_ACCESS_KEY", required=False)
    
    # Warn if only one credential is provided
    if bool(access_key_id) != bool(secret_access_key):
        logger.warning(
            "Only one of AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY is set. "
            "Both should be provided or both should be omitted (for IAM roles)."
        )
    
    return AWSConfig(
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        region=get_env_var("AWS_REGION", "us-east-2", required=False),
        s3_bucket_documents=get_env_var("S3_BUCKET_DOCUMENTS", required=True),
        s3_bucket_exports=get_env_var("S3_BUCKET_EXPORTS", required=True),
    )


def load_openai_config() -> OpenAIConfig:
    """
    Load OpenAI configuration from environment variables.
    
    Returns:
        OpenAIConfig instance
        
    Raises:
        ConfigError: If required variables are missing
    """
    return OpenAIConfig(
        api_key=get_env_var("OPENAI_API_KEY", required=True),
        model=get_env_var("OPENAI_MODEL", "gpt-4", required=False),
        temperature=get_env_float("OPENAI_TEMPERATURE", 0.7, required=False),
        max_tokens=get_env_int("OPENAI_MAX_TOKENS", 2000, required=False),
    )


def load_config() -> AppConfig:
    """
    Load and validate all configuration from environment variables.
    
    Returns:
        AppConfig instance with all configuration
        
    Raises:
        ConfigError: If required variables are missing or invalid
    """
    try:
        config = AppConfig(
            environment=get_env_var("ENVIRONMENT", "development", required=False),
            debug=get_env_bool("DEBUG", default=False, required=False),
            log_level=get_env_var("LOG_LEVEL", "INFO", required=False),
            database=load_database_config(),
            aws=load_aws_config(),
            openai=load_openai_config(),
        )
        
        # Validate configuration
        validate_config(config)
        
        logger.info(f"Configuration loaded successfully for environment: {config.environment}")
        return config
        
    except ConfigError as e:
        logger.error(f"Configuration error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading configuration: {str(e)}")
        raise ConfigError(f"Failed to load configuration: {str(e)}")


def validate_config(config: AppConfig) -> None:
    """
    Validate configuration values.
    
    Args:
        config: AppConfig instance to validate
        
    Raises:
        ConfigError: If configuration is invalid
    """
    # Validate environment
    valid_environments = ["development", "staging", "production"]
    if config.environment.lower() not in valid_environments:
        raise ConfigError(
            f"Invalid environment: {config.environment}. "
            f"Must be one of: {', '.join(valid_environments)}"
        )
    
    # Validate log level
    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if config.log_level.upper() not in valid_log_levels:
        raise ConfigError(
            f"Invalid log level: {config.log_level}. "
            f"Must be one of: {', '.join(valid_log_levels)}"
        )
    
    # Validate database configuration
    if not config.database.host:
        raise ConfigError("Database host cannot be empty")
    
    if config.database.port < 1 or config.database.port > 65535:
        raise ConfigError(f"Invalid database port: {config.database.port}")
    
    # Validate AWS configuration
    if not config.aws.s3_bucket_documents:
        raise ConfigError("S3 documents bucket name is required")
    
    if not config.aws.s3_bucket_exports:
        raise ConfigError("S3 exports bucket name is required")
    
    # Validate OpenAI configuration
    if not config.openai.api_key:
        raise ConfigError("OpenAI API key is required")
    
    if config.openai.temperature < 0 or config.openai.temperature > 2:
        raise ConfigError(f"Invalid OpenAI temperature: {config.openai.temperature}. Must be between 0 and 2")
    
    if config.openai.max_tokens < 1:
        raise ConfigError(f"Invalid OpenAI max_tokens: {config.openai.max_tokens}")
    
    logger.info("Configuration validation passed")


def get_config_summary(config: AppConfig) -> Dict[str, Any]:
    """
    Get a summary of the configuration (safe for logging, excludes secrets).
    
    Args:
        config: AppConfig instance
        
    Returns:
        Dictionary with configuration summary
    """
    return {
        "environment": config.environment,
        "debug": config.debug,
        "log_level": config.log_level,
        "database": {
            "host": config.database.host,
            "port": config.database.port,
            "name": config.database.name,
            "user": config.database.user,
        },
        "aws": {
            "region": config.aws.region,
            "s3_bucket_documents": config.aws.s3_bucket_documents,
            "s3_bucket_exports": config.aws.s3_bucket_exports,
            "credentials_configured": bool(config.aws.access_key_id and config.aws.secret_access_key),
        },
        "openai": {
            "model": config.openai.model,
            "temperature": config.openai.temperature,
            "max_tokens": config.openai.max_tokens,
            "api_key_configured": bool(config.openai.api_key),
        },
    }


# Global configuration instance
_config_instance: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """
    Get or create the global configuration instance.
    
    Returns:
        AppConfig instance
        
    Raises:
        ConfigError: If configuration cannot be loaded
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = load_config()
    return _config_instance


def reload_config() -> AppConfig:
    """
    Reload configuration from environment variables.
    Useful for testing or when environment changes.
    
    Returns:
        New AppConfig instance
    """
    global _config_instance
    _config_instance = load_config()
    return _config_instance

