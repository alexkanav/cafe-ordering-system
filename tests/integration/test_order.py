import pytest
from datetime import datetime, timezone

from infrastructure.db.models.users import Order
from domain import services
from domain import schemas
from domain.core.errors import ConflictError
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

    with pytest.raises(ConflictError):
        services.complete_order(db_session, order.id, employee_id=user_id)


def test_count__orders_exist__returns_total_count(db_session, sample_orders):
    count = services.get_orders_count(db_session)

    assert isinstance(count, int)
    assert count == 2


def test_create_order__valid_data_provided__creates_order_record(db_session):
    order_data = make_order_schema()

    dish = list(order_data.order_details.keys())[0]
    order_details = order_data.order_details[dish].model_dump()

    response = services.create_order(db_session, order_data, user_id=user_id)

    assert isinstance(response, schemas.OrderOperationResultSchema)

    db_order = db_session.get(Order, response.id)

    assert db_order.table == order_data.table
    assert db_order.final_cost == order_data.final_cost
    assert db_order.user_id == user_id
    assert db_order.original_cost == order_data.original_cost
    assert db_order.order_details == {dish: order_details}
    assert db_order.completed_at is None
    assert db_order.completed_by is None
