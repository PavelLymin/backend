from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.allergen import AllergenRead
from models.cuisine import CuisineRead
from models.recipe_ingredients import RecipeIngredientRead
from models import db_helper
from config import settings
from models import Ingredient, IngredientCreate, IngredientRead, IngredientUpdate
from models import Recipe, RecipeIngredients


router = APIRouter(
    tags=["Ingredients"],
    prefix=settings.url.ingredients,
)

ALLOWED_FIELDS = {"id", "title", "difficulty", "description", "cooking_time"}
ALLOWED_INCLUDES = {"cuisine", "ingredients", "allergens"}


@router.get("/{id}/recipes")
async def get_recipes_by_ingredient(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    id: int,
    include: Optional[str] = Query(None),
    select_fields: Optional[str] = Query(None),
):
    includes = set(include.split(",")) if include else set()
    invalid_includes = includes - ALLOWED_INCLUDES
    if invalid_includes:
        raise HTTPException(400, f"Invalid include: {invalid_includes}")

    stmt = (
        select(Recipe)
        .join(RecipeIngredients)
        .where(RecipeIngredients.ingredient_id == id)
    )

    include_options = {
        "cuisine": selectinload(Recipe.cuisine),
        "allergens": selectinload(Recipe.allergens),
        "ingredients": selectinload(Recipe.ingredients).selectinload(RecipeIngredients.ingredient),
    }

    for inc in includes:
        stmt = stmt.options(include_options[inc])

    recipes = (await session.scalars(stmt)).unique().all()

    # select
    if select_fields:
        fields = set(select_fields.split(","))
        invalid = fields - ALLOWED_FIELDS
        if invalid:
            raise HTTPException(400, f"Invalid fields: {invalid}")
    else:
        fields = ALLOWED_FIELDS

    # сборка ответа
    def serialize(recipe: Recipe):
        data = {f: getattr(recipe, f) for f in fields}

        if "cuisine" in includes:
            data["cuisine"] = (
                CuisineRead.model_validate(recipe.cuisine, from_attributes=True)
                if recipe.cuisine else None
            )

        if "allergens" in includes:
            data["allergens"] = [
                AllergenRead.model_validate(a, from_attributes=True)
                for a in recipe.allergens
            ]

        if "ingredients" in includes:
            data["ingredients"] = [
                RecipeIngredientRead.model_validate(i, from_attributes=True)
                for i in recipe.ingredients
            ]

        return data

    return [serialize(r) for r in recipes]
    

@router.get("", response_model=list[IngredientRead])
async def fetch(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
):
    stmt = select(Ingredient).order_by(Ingredient.id)
    ingredient = await session.scalars(stmt)
    return ingredient.all()


@router.post("", response_model=IngredientRead, status_code=status.HTTP_201_CREATED)
async def create(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    ingredient_create: IngredientCreate,
):
    ingredient = Ingredient(name=ingredient_create.name)
    session.add(ingredient)
    await session.commit()
    return ingredient


@router.get("/{id}", response_model=IngredientRead)
async def fetch_by_id(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    id: int,
):
    ingredient = await session.get(Ingredient, id)
    return ingredient


@router.put("/{id}", response_model=IngredientRead)
async def update(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    id: int,
    ingredient_update: IngredientUpdate,
):
    ingredient = await session.get(Ingredient, id)
    ingredient.name = ingredient_update.name
    await session.commit()
    return ingredient


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    id: int,
):
    ingredient = await session.get(Ingredient, id)
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Ingredient with id {id} not found"
        )

    await session.delete(ingredient)
    await session.commit()