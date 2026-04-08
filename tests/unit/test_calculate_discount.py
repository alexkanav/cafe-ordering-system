import pytest

from domain.core.constants import DISCOUNT_TIERS
from utils.discounts import calculate_discount


@pytest.mark.parametrize(
    "amount, expected_discount",
    [
        (DISCOUNT_TIERS[0][0] - 1, 0),
        (DISCOUNT_TIERS[0][0], DISCOUNT_TIERS[0][1]),
        (DISCOUNT_TIERS[0][0] + 1, DISCOUNT_TIERS[0][1]),
        (DISCOUNT_TIERS[1][0], DISCOUNT_TIERS[1][1]),
        (DISCOUNT_TIERS[1][0] + 1, DISCOUNT_TIERS[1][1]),
        (DISCOUNT_TIERS[2][0], DISCOUNT_TIERS[2][1]),
        (DISCOUNT_TIERS[2][0] + 1, DISCOUNT_TIERS[2][1]),
        (999999, DISCOUNT_TIERS[-1][1]),
    ]
)
def test_calculate_discount__total_amount__returns_discount(amount, expected_discount):
    assert calculate_discount(amount) == expected_discount
