import pytest
from datetime import date
from domain.rentals.date_range import DateRange


class TestDateRangeConstruction:
    def test_valid_range(self):
        start = date(2026, 5, 22)
        end = date(2026, 5, 25)
        period = DateRange(start=start, end=end)
        
        assert period.start == start
        assert period.end == end

    def test_single_day_range_is_valid(self):
        # Период в один и тот же день — это валидно (например, аренда на день)
        day = date(2026, 5, 22)
        period = DateRange(start=day, end=day)
        
        assert period.length_in_days == 0

    def test_end_before_start_raises_value_error(self):
        # Проверяем бизнес-правило: дата окончания не может быть раньше начала
        with pytest.raises(ValueError, match="end date precedes start date"):
            DateRange(start=date(2026, 5, 25), end=date(2026, 5, 22))


class TestDateRangeProperties:
    def test_length_in_days(self):
        period = DateRange(start=date(2026, 5, 22), end=date(2026, 5, 25))
        assert period.length_in_days == 3


class TestDateRangeContains:
    @pytest.fixture
    def sample_period(self):
        return DateRange(start=date(2026, 5, 22), end=date(2026, 5, 25))

    def test_contains_start_date(self, sample_period):
        assert sample_period.contains(date(2026, 5, 22))

    def test_contains_middle_date(self, sample_period):
        assert sample_period.contains(date(2026, 5, 23))

    def test_contains_end_date(self, sample_period):
        assert sample_period.contains(date(2026, 5, 25))

    def test_does_not_contain_before(self, sample_period):
        assert not sample_period.contains(date(2026, 5, 21))

    def test_does_not_contain_after(self, sample_period):
        assert not sample_period.contains(date(2026, 5, 26))


class TestDateRangeDaysRemaining:
    @pytest.fixture
    def sample_period(self):
        return DateRange(start=date(2026, 5, 22), end=date(2026, 5, 25))

    def test_days_remaining_before_period_starts(self, sample_period):
        # Если спрашиваем до начала аренды, должно вернуться полное количество дней
        assert sample_period.days_remaining_from(date(2026, 5, 20)) == 3

    def test_days_remaining_on_start_day(self, sample_period):
        assert sample_period.days_remaining_from(date(2026, 5, 22)) == 3

    def test_days_remaining_during_period(self, sample_period):
        assert sample_period.days_remaining_from(date(2026, 5, 23)) == 2

    def test_days_remaining_on_last_day(self, sample_period):
        # Формально в крайний день остаток равен 0, так как (end - day).days -> (25 - 25)
        assert sample_period.days_remaining_from(date(2026, 5, 25)) == 0

    def test_days_remaining_after_period_ends(self, sample_period):
        assert sample_period.days_remaining_from(date(2026, 5, 26)) == 0