from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# expire_on_commit=False evita el DetachedInstanceError en todos los módulos
# sin esto, después del commit SQLAlchemy expira los atributos y model_validate falla
engine = create_engine(settings.DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    expire_on_commit=False,
)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with SessionLocal() as session:
        yield session