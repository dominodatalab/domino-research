from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.orm import scoped_session, sessionmaker  # type: ignore
from sqlalchemy.ext.declarative import (  # type: ignore
    declared_attr,
    as_declarative,
)
import os

uri = os.environ.get("DATABASE_URL", "sqlite:////tmp/checkpoint.db")

# Handle Heroku / SQLAlchemy bug https://stackoverflow.com/questions/62688256/sqlalchemy-exc-nosuchmoduleerror-cant-load-plugin-sqlalchemy-dialectspostgre
uri = uri.replace("postgres://", "postgresql://")

engine = create_engine(uri)
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


@as_declarative()
class CheckpointBase:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    query = db_session.query_property()

    def __init__(self, **kwargs):
        pass


def init_db():
    # import all modules here that define models so that they are
    # registered properly on the metadata.
    import checkpoint.models  # noqa: F401

    CheckpointBase.metadata.create_all(bind=engine)


def teardown_db():
    # import all modules here that define models so that they are
    # registered properly on the metadata.
    import checkpoint.models  # noqa: F401

    CheckpointBase.metadata.drop_all(bind=engine)
