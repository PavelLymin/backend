from dishka import Provider, Scope, provide

from application.rentals.activate_rental import ActivateRentalUseCase
from application.rentals.cancel_rental import CancelRentalUseCase
from application.rentals.get_rental import GetRentalUseCase
from application.rentals.reserve_rental import ReserveRentalUseCase
from application.rentals.return_rental import ReturnRentalUseCase
from application.scooters.get_scooter import GetScooterUseCase
from domain.rentals.pricing_service import PricingService


class ServicesProvider(Provider):
    scope = Scope.REQUEST

    pricing_service = provide(PricingService)

    get_reserve_rental = provide(ReserveRentalUseCase)
    get_activate_rental = provide(ActivateRentalUseCase)
    get_return_rental = provide(ReturnRentalUseCase)
    get_cancel_rental = provide(CancelRentalUseCase)
    get_get_rental = provide(GetRentalUseCase)
    get_get_scooter = provide(GetScooterUseCase)
