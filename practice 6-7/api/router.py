from datetime import date
from fastapi import APIRouter, HTTPException, status
from dishka.integrations.fastapi import FromDishka, inject

from application.rentals.reserve_rental import ReserveRentalUseCase
from application.rentals.activate_rental import ActivateRentalUseCase
from application.rentals.return_rental import ReturnRentalUseCase
from application.rentals.cancel_rental import CancelRentalUseCase
from application.rentals.get_rental import GetRentalUseCase
from domain.rentals.rental import Rental

router = APIRouter(tags=["Rentals"])


@router.post("/rentals/reserve", status_code=status.HTTP_201_CREATED)
@inject
async def reserve_rental(
    scooter_id: int,
    user_id: int,
    start_date: date,
    end_date: date,
    use_case: FromDishka[ReserveRentalUseCase],
) -> Rental:
    try:
        return await use_case.execute(
            scooter_id=scooter_id,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/rentals/{id}/activate")
@inject
async def activate_rental(
    id: int,
    use_case: FromDishka[ActivateRentalUseCase],
) -> Rental:
    try:
        return await use_case.execute(rental_id=id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/rentals/{id}/return")
@inject
async def return_rental(
    id: int,
    use_case: FromDishka[ReturnRentalUseCase],
) -> Rental:
    try:
        return await use_case.execute(rental_id=id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/rentals/{id}/cancel")
@inject
async def cancel_rental(
    id: int,
    use_case: FromDishka[CancelRentalUseCase],
) -> Rental:
    try:
        return await use_case.execute(rental_id=id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/rentals/{id}")
@inject
async def get_rental(
    id: int,
    use_case: FromDishka[GetRentalUseCase],
) -> Rental:
    try:
        return await use_case.execute(rental_id=id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))