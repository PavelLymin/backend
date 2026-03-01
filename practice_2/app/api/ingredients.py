from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import db_helper, Ingredient, IngredientCreate, IngredientRead, IngredientUpdate, RecipeRead, Recipe, RecipeIngredients
from config import settings


router = APIRouter(
    tags=["Ingredients"],
    prefix=settings.url.ingredients,
)

@router.get("/{id}/recipes", response_model=list[RecipeRead])
async def get_recipes_by_ingredient(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    id: int,
):
    ingredient = await session.get(Ingredient, id)
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient with id {id} not found"
        )
    
    stmt = (
        select(Recipe)
        .join(RecipeIngredients)
        .where(RecipeIngredients.ingredient_id == id)
        .options(
            selectinload(Recipe.cuisine),
            selectinload(Recipe.allergens),
            selectinload(Recipe.ingredients).selectinload(RecipeIngredients.ingredient)
        )
        .order_by(Recipe.id)
    )
    
    result = await session.execute(stmt)
    recipes = result.unique().scalars().all()
    
    return recipes

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