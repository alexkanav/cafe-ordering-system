import pytest

from domain.core.constants import DISH_PREP_TIME
from utils.orders import calculate_order_lead_time


@pytest.mark.parametrize(
    "dishes, expected",
    [
        (["102"], DISH_PREP_TIME["102"]),
        (["999"], 0),
        ([], 0),
        (["101", "102", "103"], max(DISH_PREP_TIME["101"], DISH_PREP_TIME["102"], DISH_PREP_TIME["103"])),
        (["102", "999"], DISH_PREP_TIME["102"]),
    ]
)
def test_calculate_order_lead_time__multiple_dishes__returns_max_prep_time(dishes, expected):
    response = calculate_order_lead_time(dishes)
    assert isinstance(response, int)
    assert response == expected
