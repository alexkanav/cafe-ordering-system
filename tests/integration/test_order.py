from datetime import datetime, timezone

import pytest

from domain import schemas
from domain import services
from domain.core.errors import ConflictError, NotFoundError, DomainValidationError
from domain.services.order import calculate_original_cost, calculate_loyalty_pct
from infrastructure.db.models.users import Order, Dish, DishExtra
from tests.factories.order import make_order_schema

user_id = 5


@pytest.fixture
def sample_orders(db_session):
    db_session.query(Order).delete()

    order_uncompleted = Order(
        user_id=2,
        table=3,
        original_cost=100,
        final_cost=85,
        order_details={"123": {"name": "Pizza", "quantity": 1, "price": 100, "additions": {"cheese": 20}}},
    )
    order_completed = Order(
        user_id=3,
        table=4,
        original_cost=200,
        final_cost=170,
        order_details={"125": {"name": "Pasta", "quantity": 2, "price": 200, "additions": {}}},
        completed_at=datetime.now(timezone.utc),
        completed_by=1
    )

    db_session.add_all([order_uncompleted, order_completed])
    db_session.flush()

    return {"uncompleted": order_uncompleted, "completed": order_completed}


@pytest.fixture
def sample_dish(db_session):
    pizza = Dish(
        code="125",
        name="Pizza",
        category_id=1,
        price=200,
        description="Margarita",
    )

    db_session.add(pizza)
    db_session.flush()

    return pizza


@pytest.fixture
def sample_extra(db_session):
    cheese = DishExtra(
        id=11,
        name="cheese",
        price=20,
    )

    db_session.add(cheese)
    db_session.flush()

    return cheese


@pytest.mark.parametrize("only_uncompleted, expected_response", [
    (True, {(3, 85)}),
    (False, {(3, 85), (4, 170)}),
])
def test_get_orders__include_uncompleted__returns_orders(
        db_session,
        sample_orders,
        only_uncompleted,
        expected_response
):
    response = services.get_orders(db_session, only_uncompleted=only_uncompleted)

    assert all(isinstance(o, schemas.OrderSchema) for o in response)

    result_items = {(o.table, o.final_cost) for o in response}
    assert result_items == expected_response


def test_complete_order__order_uncompleted__sets_completed_fields(db_session, sample_orders):
    order = sample_orders["uncompleted"]
    services.complete_order(db_session, order.id, employee_id=user_id)

    db_session.flush()
    db_session.expire_all()
    db_order = db_session.get(Order, order.id)

    assert db_order.completed_by == user_id
    assert isinstance(db_order.completed_at, datetime)


def test_complete_order__order_already_completed__raises_conflict_error(db_session, sample_orders):
    order = sample_orders["completed"]

    with pytest.raises(ConflictError, match="Замовлення вже виконано"):
        services.complete_order(db_session, order.id, employee_id=user_id)


def test_complete_order__no_orders_exist__raises_not_found_error(db_session):
    with pytest.raises(NotFoundError, match="Замовлення не знайдено"):
        services.complete_order(db_session, 1, employee_id=user_id)


def test_get_orders_count__orders_exist__returns_total_count(db_session, sample_orders):
    count = services.get_orders_count(db_session)

    assert isinstance(count, int)
    assert count == 2


def test_get_orders_count__orders_does_not_exist__returns_zero(db_session):
    count = services.get_orders_count(db_session)

    assert count == 0


def test_calculate_original_cost__valid_data_provided__returns_original_cost(
        db_session, sample_dish, sample_extra
):
    order_data = make_order_schema()
    original_cost = calculate_original_cost(db_session, order_data.order_details)
    assert original_cost == (
            order_data.order_details["125"].quantity
            * sample_dish.price
            + sample_extra.price
    )


def test_calculate_original_cost__dish_does_not_exist__raises_not_found_error(db_session):
    order_data = make_order_schema()
    with pytest.raises(NotFoundError, match="Замовлені страви зараз недоступні"):
        services.create_order(db_session, order_data, user_id=user_id)


def test_calculate_original_cost__no_additions_exist__raises_not_found_error(db_session, sample_dish):
    order_data = make_order_schema()
    with pytest.raises(NotFoundError, match="Замовлені доповнення зараз недоступні"):
        services.create_order(db_session, order_data, user_id=user_id)


@pytest.mark.parametrize("loyalty_pct, expected", [
    (0, 0),
    (5, 5),
    (100, 100),
    (-1, 0),
    (101, 0),
])
def test_calculate_loyalty_pct__discount_value__returns_valid_discount(
        db_session, mocker, loyalty_pct, expected
):
    mocker.patch('domain.services.order.get_total_amount')
    mocker.patch(
        'domain.services.order.calculate_discount',
        return_value=loyalty_pct
    )

    result = calculate_loyalty_pct(db_session, 1)

    assert result == expected


def test_create_order__valid_data_provided__creates_order_record(db_session, mocker):
    order_data = make_order_schema()
    mock_calculate_original_cost = mocker.patch(
        'domain.services.order.calculate_original_cost',
        return_value=order_data.original_cost
    )
    mock_process_coupon = mocker.patch('domain.services.order.process_coupon', return_value=5)
    mock_calculate_loyalty_pct = mocker.patch('domain.services.order.calculate_loyalty_pct', return_value=10)
    dish = list(order_data.order_details.keys())[0]
    order_details = order_data.order_details[dish].model_dump()

    response = services.create_order(db_session, order_data, user_id=user_id)

    assert isinstance(response, schemas.OrderOperationResultSchema)

    db_order = db_session.get(Order, response.id)

    mock_calculate_original_cost.assert_called_once_with(
        db_session, order_data.order_details
    )
    mock_process_coupon.assert_called_once_with(
        db_session, order_data.coupon_code, user_id
    )
    mock_calculate_loyalty_pct.assert_called_once_with(
        db_session, user_id
    )
    assert db_order is not None
    assert db_order.table == order_data.table
    assert db_order.final_cost == order_data.final_cost
    assert db_order.user_id == user_id
    assert db_order.original_cost == order_data.original_cost
    assert db_order.loyalty_pct == 10
    assert db_order.coupon_pct == 5
    assert db_order.order_details == {dish: order_details}
    assert db_order.completed_at is None
    assert db_order.completed_by is None


def test_create_order__wrong_original_cost__raises_domain_validation_error(db_session, mocker):
    order_data = make_order_schema()
    mocker.patch(
        'domain.services.order.calculate_original_cost',
        return_value=order_data.original_cost + 1
    )

    with pytest.raises(DomainValidationError):
        services.create_order(db_session, order_data, user_id=user_id)
