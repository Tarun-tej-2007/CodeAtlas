import sys
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from alembic import context

# Add current workspace directory to sys.path to allow importing app modules
sys.path.insert(0, ".")

# Import project settings and base declarative model
from app.core.config import settings
from app.db.base import Base

# This is the Alembic Config object, which provides access to values within alembic.ini.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set model metadata for autogenerate support.
# To detect future database models, ensure they are imported in a way that registers
# them on Base.metadata before migrations run.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine, though an Engine
    is acceptable as well. By skipping engine creation, we can run migrations
    without having a live connection to the database (generating sql scripts instead).
    """
    url = settings.sqlalchemy_database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        render_as_batch=False,
        include_schemas=False,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a connection
    with the context.
    """
    # For migration runs, we construct a dedicated database connection.
    # We use NullPool since migrations are quick, short-lived tasks that do
    # not require persistent connection pooling overhead.
    connectable = create_engine(
        settings.sqlalchemy_database_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=False,
            include_schemas=False,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
