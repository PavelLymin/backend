import dataclasses
from datetime import date


@dataclasses.dataclass(frozen=True)
class DateRange:
    start: date
    end: date

    def __post_init__(self) -> None:
        if self.start > self.end:
            raise ValueError("end date precedes start date")

    @property
    def length_in_days(self) -> int:
        return (self.end - self.start).days

    def contains(self, day: date) -> bool:
        return self.start <= day <= self.end

    def days_remaining_from(self, day: date) -> int:
        if day >= self.end:
            return 0
        if day < self.start:
            return self.length_in_days
        return (self.end - day).days