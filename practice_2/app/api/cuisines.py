from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import db_helper, Cuisine, CuisineCreate, CuisineRead, CuisineUpdate
from config import settings


router = APIRouter(
    tags=["Cuisines"],
    prefix=settings.url.cuisines,
)

@router.get("", response_model=list[CuisineRead])
async def fetch(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
):
    stmt = select(Cuisine).order_by(Cuisine.id)
    cuisine = await session.scalars(stmt)
    return cuisine.all()


@router.post("", response_model=CuisineRead, status_code=status.HTTP_201_CREATED)
async def create(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    cuisine_create: CuisineCreate,
):
    cuisine = Cuisine(name=cuisine_create.name)
    session.add(cuisine)
    await session.commit()
    return cuisine


@router.get("/{id}", response_model=CuisineRead)
async def fetch_by_id(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    id: int,
):
    cuisine = await session.get(Cuisine, id)
    return cuisine


@router.put("/{id}", response_model=CuisineRead)
async def update(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    id: int,
    cuisine_update: CuisineUpdate,
):
    cuisine = await session.get(Cuisine, id)
    cuisine.name = cuisine_update.name
    await session.commit()
    return cuisine


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    id: int,
):
    cuisine = await session.get(Cuisine, id)
    if not cuisine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Cuisine with id {id} not found"
        )

    await session.delete(cuisine)
    await session.commit()