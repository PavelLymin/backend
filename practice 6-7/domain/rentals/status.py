from enum import Enum


class RentalStatus(str, Enum):
    RESERVED = "RESERVED"
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
    CANCELLED = "CANCELLED"
