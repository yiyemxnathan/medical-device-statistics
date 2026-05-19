from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings


def engine_kwargs(database_url: str) -> dict[str, object]:
    if database_url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {}


engine = create_engine(settings.database_url, **engine_kwargs(settings.database_url))


def create_db_and_tables() -> None:
    import app.models.records  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
