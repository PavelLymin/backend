from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from pydantic import BaseModel
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.tables import Recipe
from .base import Base

class AuthorRead(BaseModel):
    id: int


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    recipes: Mapped[list["Recipe"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan"
    )
