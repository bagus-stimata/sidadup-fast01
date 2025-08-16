import sqlalchemy
from sqlalchemy import create_engine as _sa_create_engine
from sqlalchemy.event import listen


def _patched_create_engine(*args, **kwargs):
    """Wrapper around SQLAlchemy's ``create_engine``.

    For SQLite connections we automatically attach a ``public`` schema alias so
    that SQL statements referencing ``public.<table>`` work just like in
    PostgreSQL.  This mimics the behaviour implemented in ``app.core.database``
    and keeps the test suite agnostic of the actual database backend.
    """
    engine = _sa_create_engine(*args, **kwargs)
    if engine.url.get_backend_name().startswith("sqlite"):
        # Apply schema translation so "public" maps to the default schema
        engine.update_execution_options(schema_translate_map={"public": None})
        db_path = engine.url.database

        def _on_connect(dbapi_connection, connection_record):
            dbapi_connection.execute(f"ATTACH DATABASE '{db_path}' AS public")

        listen(engine, "connect", _on_connect)
    return engine

# Override SQLAlchemy's factory with the patched version
sqlalchemy.create_engine = _patched_create_engine
