import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from dotenv import load_dotenv

from alembic import context

# Load environment variables from .env file
# Try .env.production first (for production), then fall back to .env (for development)
# Look in the backend directory (parent of alembic directory)
# backend_dir = os.path.dirname(os.path.dirname(__file__))
# env_file = os.getenv("DOTENV_FILE")
# if not env_file:
#     # Try .env.production first, then .env
#     prod_env = os.path.join(backend_dir, ".env.production")
#     dev_env = os.path.join(backend_dir, ".env")
#     if os.path.exists(prod_env):
#         env_file = prod_env
#     else:
#         env_file = dev_env
# else:
#     # If DOTENV_FILE is set, use it (can be relative or absolute)
#     if not os.path.isabs(env_file):
#         env_file = os.path.join(backend_dir, env_file)
# load_dotenv(env_file)
load_dotenv()

# Add the backend directory to the path so we can import shared modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Construct database URL from environment variables
# Use .env as the source of truth for all database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "demand_letters")
DB_USER = os.getenv("DB_USER", "dev_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "dev_password")
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Import Base and models (without importing engine to avoid connection attempt)
from shared.base import Base
from shared.models import (
    Firm,
    User,
    Document,
    LetterTemplate,
    GeneratedLetter,
    LetterSourceDocument,
)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set database URL from environment variables
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
