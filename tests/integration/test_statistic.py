import pytest
from datetime import date, timedelta

from infrastructure.db.models.admin import SalesSummary, DishOrdersStats
from domain import services, schemas

today = date.today()
yesterday = today - timedelta(days=1)
day_before_yesterday = today - timedelta(days=2)

@pytest.fixture
def sample_sales(db_session):
    db_session.add_all([
        SalesSummary(date=day_before_yesterday, total_sales=500, orders=2, returning_customers=1),
        SalesSummary(date=yesterday, total_sales=1000, orders=6, returning_customers=2),
        SalesSummary(date=today, total_sales=0, orders=0, returning_customers=0),
    ])
    db_session.flush()


@pytest.fixture
def sample_dish_orders_stats(db_session):
    db_session.add_all([
        DishOrdersStats(code="A1", orders=10),
        DishOrdersStats(code="B2", orders=20),
        DishOrdersStats(code="C3", orders=5),
        DishOrdersStats(code="D5", orders=10),
    ])
    db_session.flush()


@pytest.mark.parametrize("days, expected_result", [
    (0, ([1000.0], [6], [2], [166.67])),
    (1, ([500, 1000, 0], [2, 6, 0], [1, 2, 0], [250.0, 166.67, 0.0])),
    (5, ([500, 1000, 0], [2, 6, 0], [1, 2, 0], [250.0, 166.67, 0.0])),
    (-5, ([], [], [], [])),
])
def test_get_sales_summary__various_day_ranges__returns_correct_summary(db_session, sample_sales, days, expected_result):
    start_date = yesterday - timedelta(days=days)
    end_date = yesterday + timedelta(days=days)

    response = services.get_sales_summary(db_session, start_date=start_date, end_date=end_date)

    assert isinstance(response, schemas.SalesSummarySchema)

    actual = (response.total_sales, response.orders, response.returning_customers, response.avg_check_sizes)
    assert actual == expected_result


def test_get_sales_summary__date_formatting__returns_dd_mm(db_session, sample_sales):
    response = services.get_sales_summary(db_session, start_date=yesterday, end_date=today)
    for d in response.dates:
        # Ensure date format is exactly "dd-mm"
        day, month = d.split("-")
        assert len(day) == 2 and len(month) == 2
        assert 1 <= int(day) <= 31
        assert 1 <= int(month) <= 12


@pytest.mark.parametrize("limit, expected_result", [
    (0, ([], [])),
    (2, (["B2", "A1"], [20, 10])),
    (100, (["B2", "A1", "D5", "C3"], [20, 10, 10, 5])),
])
def test_get_dish_order_stats__limit_variants__returns_top_dishes(
        db_session,
        sample_dish_orders_stats,
        limit,
        expected_result,
):
    response = services.get_dish_order_stats(db_session, limit=limit)
    assert isinstance(response, schemas.DishOrderStatsSchema)
    assert (response.dishes, response.orders) == expected_result

