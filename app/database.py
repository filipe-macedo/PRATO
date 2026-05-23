from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import configuracoes

_connect_args = (
    {"check_same_thread": False}
    if configuracoes.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(
    configuracoes.database_url,
    connect_args=_connect_args,
    echo=configuracoes.debug,
)

if configuracoes.database_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _habilitar_fk(dbapi_conn, _):
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass
