import pytest
from datetime import datetime, date, timedelta

from domain.core.errors import ConflictError, DomainValidationError, NotFoundError
from infrastructure.db.models.users import Coupon
from tests.factories.coupon import make_coupon_schema
from domain import services


@pytest.fixture
def sample_coupons(db_session):
    db_session.query(Coupon).delete()
    db_session.flush()

    today = date.today()

    not_expired = today + timedelta(days=1)
    expired = today - timedelta(days=1)

    coupon1 = Coupon(code="C1", discount_value=10, expires_at=not_expired)
    coupon2 = Coupon(code="C2", discount_value=7)
    coupon3 = Coupon(code="C3", discount_value=5, expires_at=expired)
    coupon4 = Coupon(code="C4", discount_value=10, is_active=False, expires_at=not_expired)

    db_session.add_all([coupon1, coupon2, coupon3, coupon4])
    db_session.flush()

    return {
        "c1": coupon1,
        "c2": coupon2,
        "c3": coupon3,
        "c4": coupon4,
    }


def test_create_coupon__no_code__generates_unique_code(db_session):
    first_id = services.create_coupon(db_session, make_coupon_schema(code=None))
    second_id = services.create_coupon(db_session, make_coupon_schema(code=None))

    first_coupon = db_session.get(Coupon, first_id)
    second_coupon = db_session.get(Coupon, second_id)

    assert first_coupon.code is not None
    assert second_coupon.code is not None
    assert first_coupon.code != second_coupon.code


def test_create_coupon__code_provided__uses_given_code(db_session):
    code = "TEST5"
    discount_value = 7
    coupon_id = services.create_coupon(db_session, make_coupon_schema(code=code, discount_value=discount_value))

    db_coupon = db_session.get(Coupon, coupon_id)

    assert db_coupon.code == code
    assert db_coupon.discount_value == discount_value
    assert db_coupon.is_active is True


@pytest.mark.parametrize("expires_at", [
    "2025-10-30",
    None,
])
def test_create_coupon__expires_at_variants__stores_correct_value(db_session, expires_at):
    data = make_coupon_schema(expires_at=expires_at)

    coupon_id = services.create_coupon(db_session, data)

    db_coupon = db_session.get(Coupon, coupon_id)

    assert db_coupon.discount_value == data.discount_value
    assert db_coupon.is_active is True

    expected = date.fromisoformat(expires_at) if expires_at else None
    assert db_coupon.expires_at == expected


def test_create_coupon__code_already_exists__raises_conflict_error(db_session, sample_coupons):
    with pytest.raises(ConflictError):
        services.create_coupon(db_session, make_coupon_schema(code="C1"))


def test_get_coupons__active_and_not_expired__returns_only_valid_coupons(db_session, sample_coupons):
    response = services.get_coupons(db_session)

    codes = {(c.code, c.discount_value) for c in response}
    assert codes == {("C1", 10), ("C2", 7)}


def test_deactivate_coupon__coupon_is_active__sets_is_active_to_false(db_session, sample_coupons):
    coupon = sample_coupons["c1"]

    services.deactivate_coupon(db_session, coupon.id)
    db_coupon = db_session.get(Coupon, coupon.id)

    assert db_coupon.is_active is False


def test_deactivate_coupon__coupon_does_not_exist__raises_not_found_error(db_session):
    with pytest.raises(NotFoundError):
        services.deactivate_coupon(db_session, 1)


def test_deactivate_coupon__coupon_already_inactive__raises_conflict_error(db_session, sample_coupons):
    with pytest.raises(ConflictError):
        services.deactivate_coupon(db_session, sample_coupons["c4"].id)


def test_check_coupon__valid_coupon__returns_discount_and_marks_as_used(db_session, sample_coupons):
    coupon = services.check_coupon(db_session, coupon_code="C1", user_id=1)
    assert coupon == 10
    db_session.flush()
    db_coupon = db_session.get(Coupon, sample_coupons["c1"].id)
    assert db_coupon.is_active is False
    assert db_coupon.user_id == 1
    assert isinstance(db_coupon.used_at, datetime)


@pytest.mark.parametrize("code, error", [
    ("C9", NotFoundError),
    ("C4", ConflictError),
    ("C3", DomainValidationError),
])
def test_check_coupon__invalid_cases__raises_errors(db_session, sample_coupons, code, error):
    with pytest.raises(error):
        services.check_coupon(db_session, coupon_code=code, user_id=1)
