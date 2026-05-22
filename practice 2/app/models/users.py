from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from pydantic import BaseModel
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.tables import Recipe
from .base import Base

class AuthorRead(BaseModel):
    id: int
    first_name: str
    last_name: str


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name:  Mapped[str] = mapped_column(String(128))
    last_name:  Mapped[str] = mapped_column(String(128))

    recipes: Mapped[list["Recipe"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan"
    )
