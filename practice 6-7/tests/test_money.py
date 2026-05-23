import pytest
from decimal import Decimal
from domain.shared.money import Money


class TestMoneyConstruction:
    def test_zero(self):
        assert Money.zero().amount_minor == 0
        assert Money.zero().is_zero()

    def test_from_major_int(self):
        m = Money.from_major(100)
        assert m.amount_minor == 10_000
        assert m.amount == Decimal("100.00")

    def test_from_major_decimal(self):
        m = Money.from_major(Decimal("9.99"))
        assert m.amount_minor == 999

    def test_amount_returns_two_digits(self):
        m = Money(amount_minor=12345)
        assert m.amount == Decimal("123.45")


class TestMoneyArithmetic:
    def test_add(self):
        result = Money.from_major(10) + Money.from_major(5)
        assert result == Money.from_major(15)

    def test_sub_throws_error_on_negative(self):
        with pytest.raises(ValueError):
            _ = Money.from_major(10) - Money.from_major(15)

    def test_multiply_by_int(self):
        result = Money.from_major(100) * 3
        assert result == Money.from_major(300)

    def test_multiply_by_fraction_rounds_half_up(self):
        result = Money(amount_minor=100) * Decimal("0.333")
        assert result.amount_minor == 33

    def test_multiply_zero_stays_zero(self):
        assert (Money.zero() * 5).is_zero()


class TestMoneyPredicates:
    def test_is_zero(self):
        assert Money.zero().is_zero()
        assert not Money.from_major(1).is_zero()
