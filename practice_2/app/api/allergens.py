from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import db_helper, Allergen, AllergenCreate, AllergenRead, AllergenUpdate
from config import settings


router = APIRouter(
    tags=["Allergens"],
    prefix=settings.url.allergens,
)

@router.get("", response_model=list[AllergenRead])
async def fetch(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
):
    stmt = select(Allergen).order_by(Allergen.id)
    allergen = await session.scalars(stmt)
    return allergen.all()


@router.post("", response_model=AllergenRead, status_code=status.HTTP_201_CREATED)
async def create(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    allergen_create: AllergenCreate,
):
    allergen = Allergen(name=allergen_create.name)
    session.add(allergen)
    await session.commit()
    return allergen


@router.get("/{id}", response_model=AllergenRead)
async def fetch_by_id(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    id: int,
):
    allergen = await session.get(Allergen, id)
    return allergen


@router.put("/{id}", response_model=AllergenRead)
async def update(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    id: int,
    allergen_update: AllergenUpdate,
):
    allergen = await session.get(Allergen, id)
    allergen.name = allergen_update.name
    await session.commit()
    return allergen


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    id: int,
):
    allergen = await session.get(Allergen, id)
    if not allergen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Allergen with id {id} not found"
        )

    await session.delete(allergen)
    await session.commit()