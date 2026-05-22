from enum import Enum


class ScooterCondition(str, Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    WORN = "WORN"