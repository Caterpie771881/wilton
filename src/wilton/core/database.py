from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine

__all__ = ["db", "init_db"]


db = create_engine("sqlite:///:memory:")


def init_db(db: Engine):
    SQLModel.metadata.create_all(db)
