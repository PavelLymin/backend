from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.types import TypeDecorator, Integer as IntegerType

import enum
from enum import IntEnum
from .base import Base

if TYPE_CHECKING:
    from .users import User


class MeasurementEnum(IntEnum):
    GRAMS = 1
    PIECES = 2
    MILLILITERS = 3

    @property
    def label(self) -> str:
        return {
            MeasurementEnum.GRAMS: "г",
            MeasurementEnum.PIECES: "шт",
            MeasurementEnum.MILLILITERS: "мл",
        }[self]
    

class CastIntEnum(TypeDecorator):
    impl = IntegerType
    cache_ok = True

    def __init__(self, enumtype, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value, dialect):
        if isinstance(value, enum.Enum):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self._enumtype(value)


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    cuisine_id: Mapped[int] = mapped_column(ForeignKey("cuisines.id"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    cooking_time: Mapped[int] = mapped_column(Integer)
    difficulty: Mapped[int] = mapped_column(Integer, default=1)
    cuisine: Mapped["Cuisine"] = relationship(back_populates="recipes")
    allergens: Mapped[list["Allergen"]] = relationship(secondary="recipe_allergens", back_populates="recipes")
    ingredients: Mapped[list["RecipeIngredients"]] = relationship(back_populates="recipe", cascade="all, delete-orphan")

    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    author: Mapped["User"] = relationship(back_populates="recipes")


    def __repr__(self):
        return f'''Recipe(id={self.id}, 
        cuisine={self.cuisine_id}, 
        title={self.title}, 
        description={self.description}, 
        cooking_time={self.cooking_time}, 
        difficulty={self.difficulty}'''
    

class Cuisine(Base):
    __tablename__ = "cuisines"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    recipes: Mapped["Recipe"] = relationship(back_populates="cuisine")

    def __repr__(self):
        return f'''Cuisine(id={self.id}, 
        name={self.name})'''
    

class Allergen(Base):
    __tablename__ = "allergens"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    recipes: Mapped["Recipe"] = relationship(secondary="recipe_allergens", back_populates="allergens")

    def __repr__(self):
        return f'''Allergen(id={self.id}, 
        title={self.name})'''


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    recipe_ingredients: Mapped[list["RecipeIngredients"]] = relationship(back_populates="ingredient")

    def __repr__(self):
        return f'''Ingredient(id={self.id}, 
        title={self.name})'''


class RecipeAllergens(Base):
    __tablename__ = "recipe_allergens"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True)
    allergen_id: Mapped[int] = mapped_column(ForeignKey("allergens.id", ondelete="CASCADE"), primary_key=True)

    def __repr__(self):
        return f'''RecipeAllergens(recipe_id={self.recipe_id}, 
        allergen_id={self.allergen_id})'''


class RecipeIngredients(Base):
    __tablename__ = "recipe_ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"))
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id", ondelete="CASCADE"))
    quantity: Mapped[int] = mapped_column(Integer)
    measurement: Mapped[MeasurementEnum] = mapped_column(CastIntEnum(MeasurementEnum), nullable=False)
    
    recipe: Mapped["Recipe"] = relationship(back_populates="ingredients")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="recipe_ingredients")

    @property
    def name(self) -> str:
        return self.ingredient.name if self.ingredient else ""

    def __repr__(self):
        return f'''RecipeIngredients(id={self.id}, 
        recipe={self.recipe_id}, 
        ingredient={self.ingredient_id}, 
        quantity={self.quantity}, 
        measurement={self.measurement})'''