from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    amount_minor: int

    def __post_init__(self):
        if self.amount_minor < 0:
            raise ValueError("Money amount cannot be negative")

    @property
    def amount(self) -> Decimal:
        return (Decimal(self.amount_minor) / 100).quantize(Decimal("0.01"))

    @classmethod
    def from_major(cls, major: Decimal | float | int) -> "Money":
        amount_minor = int(Decimal(str(major)) * 100)
        return cls(amount_minor)

    @classmethod
    def zero(cls) -> "Money":
        return cls(0)

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        return Money(amount_minor=self.amount_minor + other.amount_minor)

    def __sub__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        result = self.amount_minor - other.amount_minor
        if result < 0:
            raise ValueError("Subtraction would result in negative money")
        return Money(amount_minor=result)

    def __mul__(self, multiplier: int | float) -> "Money":
        if isinstance(multiplier, (int, float)):
            return Money(amount_minor=int(self.amount_minor * multiplier))
        return NotImplemented

    def __rmul__(self, multiplier: int | float) -> "Money":
        return self.__mul__(multiplier)

    def __truediv__(self, divisor: int | float) -> "Money":
        if isinstance(divisor, (int, float)):
            return Money(amount_minor=int(self.amount_minor / divisor))
        return NotImplemented

    def __lt__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount_minor < other.amount_minor

    def __le__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount_minor <= other.amount_minor

    def __gt__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount_minor > other.amount_minor

    def __ge__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount_minor >= other.amount_minor

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount_minor == other.amount_minor

    def is_zero(self) -> bool:
        return self.amount_minor == 0
    