import json

from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated, Optional
from sqlalchemy.orm import contains_eager, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate 
from fastapi_filter import FilterDepends, with_prefix
from fastapi_filter.contrib.sqlalchemy import Filter
from tasks.recipe_generation import generate_recipe_task
from models.users import User
from authentication.fastapi_users import current_active_user
from pydantic import BaseModel, Field

from config import settings 
from models import db_helper
from models import Recipe, RecipeCreate, RecipeUpdate, RecipeFullRead
from models import Allergen, Ingredient, Cuisine, RecipeIngredients

from openai import AsyncOpenAI


class RecipeGenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Описание желаемого рецепта")


class RecipeGenerateResponse(BaseModel):
    status: str = Field(..., description="Статус обработки запроса")
    message: str = Field(default="Генерация началась", description="Сообщение")


client = AsyncOpenAI(
    api_key=settings.api.router_key,
    base_url="https://openrouter.ai/api/v1",
)

router = APIRouter(
    tags=["Recipes"],
    prefix=settings.url.recipes,
)


class IngredientFilter(Filter):
    id__in: Optional[list[int]] = None

    class Constants(Filter.Constants):
        model = Ingredient


class RecipeIngredientFilter(Filter):
    ingredient: Optional[IngredientFilter] = FilterDepends(
        with_prefix("ingredient", IngredientFilter)
    )

    class Constants(Filter.Constants):
        model = RecipeIngredients


class RecipeFilter(Filter):
    title__like: Optional[str] = None
    ingredients: Optional[RecipeIngredientFilter] = FilterDepends(
        with_prefix("ingredients", RecipeIngredientFilter)
    )
    order_by: Optional[list[str]] = None

    class Constants(Filter.Constants):
        model = Recipe


@router.post("/generate", response_model=RecipeGenerateResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_recipe(
    request: RecipeGenerateRequest,
    user: User = Depends(current_active_user),
):
    await generate_recipe_task.kiq(
        prompt=request.prompt,
        user_id=user.id,
    )
    
    return RecipeGenerateResponse(
        status="queued",
        message="Генерация рецепта началась. Результат будет доступен в ближайшее время.",
    )


@router.get("", response_model=Page[RecipeFullRead])
async def fetch(
    filter: Annotated[RecipeFilter, FilterDepends(RecipeFilter)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    stmt = (
        select(Recipe)
        .outerjoin(Recipe.cuisine)
        .outerjoin(Recipe.author)
        .outerjoin(Recipe.allergens)
        .outerjoin(Recipe.ingredients)
        .outerjoin(RecipeIngredients.ingredient)
        .options(
            contains_eager(Recipe.cuisine),
            contains_eager(Recipe.author),
            contains_eager(Recipe.allergens),
            contains_eager(Recipe.ingredients).contains_eager(RecipeIngredients.ingredient),
        )
        .distinct()
    )

    stmt = filter.sort(stmt)
    stmt = filter.filter(stmt)
    return await paginate(session, stmt)

@router.get("/{id}", response_model=RecipeFullRead)
async def fetch_one(
    id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    stmt = (
        select(Recipe)
        .where(Recipe.id == id)
        .outerjoin(Recipe.cuisine)
        .outerjoin(Recipe.author)
        .outerjoin(Recipe.allergens)
        .outerjoin(Recipe.ingredients)
        .outerjoin(RecipeIngredients.ingredient)
        .options(
            contains_eager(Recipe.cuisine),
            contains_eager(Recipe.author),
            contains_eager(Recipe.allergens),
            contains_eager(Recipe.ingredients).contains_eager(RecipeIngredients.ingredient),
        )
        .distinct()
    )

    recipe = await session.scalar(stmt)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {id} not found",
        )
    return recipe

@router.post("", response_model=RecipeFullRead, status_code=status.HTTP_201_CREATED)
async def create(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    recipe_create: RecipeCreate,
    user: User = Depends(current_active_user),
):
    cuisine = await session.get(Cuisine, recipe_create.cuisine_id)
    if not cuisine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cuisine with id {recipe_create.cuisine_id} not found",
        )

    allergens = []
    if recipe_create.allergen_ids:
        allergens = await session.scalars(
            select(Allergen).where(Allergen.id.in_(recipe_create.allergen_ids))
        )
        allergens = allergens.all()

    recipe_ingredients = []
    if recipe_create.ingredients:
        ingredient_ids = {item.ingredient_id for item in recipe_create.ingredients}
        ingredients = await session.scalars(
            select(Ingredient).where(Ingredient.id.in_(ingredient_ids))
        )
        ingredients_map = {item.id: item for item in ingredients.all()}

        missing_ids = ingredient_ids - set(ingredients_map.keys())
        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ingredients not found: {missing_ids}",
            )

        recipe_ingredients = [
            RecipeIngredients(
                ingredient=ingredients_map[item.ingredient_id],
                quantity=item.quantity,
                measurement=item.measurement,
            )
            for item in recipe_create.ingredients
        ]

    recipe = Recipe(
        cuisine_id=recipe_create.cuisine_id,
        title=recipe_create.title,
        description=recipe_create.description,
        cooking_time=recipe_create.cooking_time,
        difficulty=recipe_create.difficulty,
        allergens=allergens,
        ingredients=recipe_ingredients,
        author_id=user.id
    )

    session.add(recipe)
    await session.commit()

    stmt = (
        select(Recipe)
        .where(Recipe.id == recipe.id)
        .options(
            selectinload(Recipe.cuisine),
            selectinload(Recipe.allergens),
            selectinload(Recipe.ingredients).selectinload(RecipeIngredients.ingredient),
        )
    )
    recipe = await session.scalar(stmt)
    return recipe


@router.put("/{id}", response_model=RecipeFullRead)
async def update(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    id: int,
    recipe_update: RecipeUpdate,
    user: User = Depends(current_active_user),
):
    
    recipe = await session.get(Recipe, id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {id} not found",
        )

    if recipe.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the author of this recipe",
        )
    
    recipe.title = recipe_update.title
    recipe.description = recipe_update.description
    recipe.cooking_time = recipe_update.cooking_time
    recipe.difficulty = recipe_update.difficulty
    recipe.cuisine_id = recipe_update.cuisine_id

    await session.commit()
    stmt = (
        select(Recipe)
        .where(Recipe.id == id)
        .options(
            selectinload(Recipe.cuisine),
            selectinload(Recipe.allergens),
            selectinload(Recipe.ingredients).selectinload(RecipeIngredients.ingredient)
        )
    )
    recipe = await session.scalar(stmt)
    return recipe


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    id: int,
    user: User = Depends(current_active_user),
):
    recipe = await session.get(Recipe, id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {id} not found",
        )

    if recipe.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the author of this recipe",
        )

    await session.delete(recipe)
    await session.commit()