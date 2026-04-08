import pytest
from sqlalchemy.exc import IntegrityError

from domain import services
from infrastructure.db.models.admin import Staff
from tests.factories.register import make_register_schema, make_login_schema

email = "test@test.com"
name = "admin"


def test_register_staff__valid_data__returns_persisted_staff_id(db_session):
    user_id = services.register_staff(db_session, make_register_schema(email=email))

    user = db_session.get(Staff, user_id)
    assert user.name == name
    assert user.email == email


def test_register_staff__email_already_exists__raises_integrity_error(db_session):
    services.register_staff(db_session, make_register_schema(email=email))
    with pytest.raises(IntegrityError):
        services.register_staff(db_session, make_register_schema(email=email))


def test_authenticate_staff__valid_credentials__returns_staff(db_session, create_staff_user):
    create_staff_user(email=email)

    user = services.authenticate_staff(db_session, make_login_schema(email=email))
    assert user.name == name


def test_authenticate_staff__incorrect_password__return_none(db_session, create_staff_user):
    create_staff_user(email=email, password="1234")

    user = services.authenticate_staff(db_session, make_login_schema(email=email, password="1111"))
    assert user is None


def test_authenticate_staff__email_not_exist__return_none(db_session):
    user = services.authenticate_staff(db_session, make_login_schema(email=email))
    assert user is None
