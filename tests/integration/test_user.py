import pytest
from decimal import Decimal

from infrastructure.db.models.users import User, Order
from domain import services
from utils.enums import UserRole


@pytest.fixture
def sample_users(create_staff_user, create_client_user):
    user1 = create_client_user(id=101)
    user2 = create_client_user(id=102)
    user11 = create_staff_user(email="service@test.com")

    return {"user1": user1, "user2": user2, "user11": user11}


@pytest.fixture
def sample_orders(db_session, sample_users):
    def make_order(user_id, original_cost, final_cost, order_details=None):
        if order_details is None:
            order_details = {
                "123": {
                    "name": "Pizza",
                    "quantity": 1,
                    "price": 100,
                    "additions": {},
                }
            }

        return Order(
            user_id=user_id,
            original_cost=original_cost,
            final_cost=final_cost,
            order_details=order_details,
        )

    order1 = make_order(sample_users["user1"].id, 100, 80)
    order2 = make_order(sample_users["user2"].id, 200, 170)
    order3 = make_order(sample_users["user1"].id, 150, 130)

    db_session.add_all([order1, order2, order3])
    db_session.flush()

    return [order1, order2, order3]


def test_create_user__valid_call__returns_persisted_user_id(db_session):
    user_id = services.create_user(db_session)
    user = db_session.get(User, user_id)
    assert user is not None
    assert user.id == user_id


def test_sessions__user_has_two_orders__returns_two(db_session, sample_orders, sample_users):
    count = services.get_user_sessions_count(db_session, sample_users["user1"].id)
    assert isinstance(count, int)
    assert count == 2


def test_sessions__user_without_orders__returns_zero(db_session, sample_users):
    count = services.get_user_sessions_count(db_session, sample_users["user1"].id)
    assert count == 0


def test_total_amount__user_has_orders__returns_sum_of_final_cost(db_session, sample_orders, sample_users):
    amount = services.get_total_amount(db_session, sample_users["user1"].id)
    assert isinstance(amount, Decimal)
    assert amount == Decimal("210")


def test_total_amount__user_without_orders__returns_zero(db_session, sample_users):
    amount = services.get_total_amount(db_session, sample_users["user1"].id)
    assert amount == Decimal("0")


@pytest.mark.parametrize(
    "user_key, role, expected_result",
    [
        ("user1", UserRole.client, True),
        ("user11", UserRole.staff, True),
        ("user1", UserRole.staff, False),
        ("user11", UserRole.client, False),
        ("nonexistent", UserRole.client, False),
    ],
)
def test_user_exists_for_role__given_user_and_role__returns_expected(
        db_session,
        sample_users,
        user_key,
        role,
        expected_result,
):
    user = sample_users.get(user_key)

    non_existent_user_id = 999
    user_id = user.id if user else non_existent_user_id

    result = services.user_exists_for_role(db_session, user_id, role)

    assert result is expected_result
