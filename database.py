from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

SQLALCHEMY_DATABASE_URL = "sqlite:///./db.sqlite3"

connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith('sqlite') else {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False, future=True, connect_args=connect_args)

SessionLokal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLokal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    import models
    Base.metadata.create_all(bind=engine)
