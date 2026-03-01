from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from models import db_helper, Recipe, RecipeCreate, RecipeUpdate, RecipeRead, Allergen, Ingredient, RecipeIngredients, RecipeAllergens
from config import settings
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter(
    tags=["Recipes"],
    prefix=settings.url.recipes,
)

@router.get("", response_model=list[RecipeRead])
async def fetch(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
):
    stmt = (
        select(Recipe)
        .options(
            selectinload(Recipe.cuisine),
            selectinload(Recipe.allergens),
            selectinload(Recipe.ingredients)
            .selectinload(RecipeIngredients.ingredient)
        )
        .order_by(Recipe.id)
    )
    
    result = await session.execute(stmt) 
    recipes = result.scalars().all()
    return recipes


@router.post("", response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
async def create(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    recipe_create: RecipeCreate,
):
    recipe = Recipe(
        cuisine_id=recipe_create.cuisine_id,
        title=recipe_create.title, 
        description=recipe_create.description, 
        cooking_time=recipe_create.cooking_time, 
        difficulty=recipe_create.difficulty)
    
    session.add(recipe)
    await session.flush()
    
    await __add_allergens(session, recipe_create, recipe)
    await __add_ingredients(session, recipe_create, recipe)    
    await session.commit()
    stmt = (
        select(Recipe)
        .where(Recipe.id == recipe.id)
        .options(
            selectinload(Recipe.allergens),  
            selectinload(Recipe.ingredients)  
            .selectinload(RecipeIngredients.ingredient) 
        )
    )    
    recipe = await session.scalar(stmt)
    return recipe

async def __add_allergens(session, recipe_create, recipe):
    allergens =  await session.scalars(select(Allergen).where(Allergen.id.in_(recipe_create.allergen_ids)))
    for allergen in allergens.all():
        recipe_allergen = RecipeAllergens(
            recipe_id=recipe.id,
            allergen_id=allergen.id
        )
        session.add(recipe_allergen)


async def __add_ingredients(session, recipe_create, recipe):
    for ing_data in recipe_create.ingredients:
        ing = await session.get(Ingredient, ing_data.ingredient_id)
        if not ing:
            raise HTTPException(404, f"Ingredient {ing_data.ingredient_id} not found")
        recipe_ing = RecipeIngredients(
            recipe=recipe,
            ingredient=ing,
            quantity=ing_data.quantity,
            measurement=ing_data.measurement
        )
        session.add(recipe_ing)


@router.put("/{id}", response_model=RecipeRead)
async def update(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    id: int,
    recipe_update: RecipeUpdate,
):
    recipe = await session.get(Recipe, id)
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
):
    recipe = await session.get(Recipe, id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Recipe with id {id} not found"
        )

    await session.delete(recipe)
    await session.commit()