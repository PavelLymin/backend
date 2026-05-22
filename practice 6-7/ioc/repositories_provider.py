from dishka import Provider, Scope, provide

from domain.rentals.repository import IRentalRepository
from domain.scooters.repository import IScooterRepository
from infrastructure.repositories.rental_repository import RentalRepositoryImpl
from infrastructure.repositories.scooter_repository import ScooterRepositoryImpl



class RepositoriesProvider(Provider):
    scope = Scope.REQUEST

    rental_repo = provide(source=RentalRepositoryImpl, provides=IRentalRepository)
    scooter_repo = provide(source=ScooterRepositoryImpl, provides=IScooterRepository)
