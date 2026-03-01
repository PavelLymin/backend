from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from models import db_helper, Recipe, RecipeCreate, RecipeUpdate, RecipeRead
from config import settings
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
    stmt = select(Recipe).order_by(Recipe.id)
    posts = await session.scalars(stmt)
    return posts.all()


@router.post("", response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
async def create(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    post_create: RecipeCreate,
):
    recipe = Recipe(title=post_create.title, 
                      description=post_create.description, 
                      cooking_time=post_create.cooking_time, 
                      difficulty=post_create.difficulty)
    session.add(recipe)
    await session.commit()
    return recipe


@router.get("/{id}", response_model=RecipeRead)
async def fetch_by_id(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    id: int,
):
    post = await session.get(Recipe, id)
    return post


@router.put("/{id}", response_model=RecipeRead)
async def update(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    id: int,
    post_update: RecipeUpdate,
):
    post = await session.get(Recipe, id)
    post.title = post_update.title
    await session.commit()
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    id: int,
):
    post = await session.get(Recipe, id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found"
        )

    await session.delete(post)
    await session.commit()