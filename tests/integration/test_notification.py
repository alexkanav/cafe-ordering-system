import pytest
from datetime import datetime

from infrastructure.db.models.admin import AdminNotification
from domain import services
from domain import schemas
from domain.core.errors import NotFoundError


@pytest.fixture
def sample_notif(db_session):
    notif_read = AdminNotification(title="T1", message="M1", is_read=True)
    notif_unread = AdminNotification(title="T2", message="M2")

    db_session.add_all([notif_read, notif_unread])
    db_session.flush()

    return {"N1": notif_read, "N2": notif_unread}


@pytest.mark.parametrize("only_unread, expected_response", [
    (False, {("T1", "M1"), ("T2", "M2")}),
    (True, {("T2", "M2")}),
])
def test_get_notifications__include_read__returns_notifications(
        db_session,
        sample_notif,
        only_unread,
        expected_response
):
    response = services.get_notifications(only_unread, db_session)

    assert all(isinstance(n, schemas.NotificationSchema) for n in response)

    result = {(n.title, n.message) for n in response}
    assert result == expected_response


def test_count_unread_notifications__unread_exist__returns_correct_count(db_session, sample_notif):
    count = services.count_unread_notifications(db_session)
    assert isinstance(count, int)
    assert count == 1


def test_mark_notification_as_read__notification_exists__sets_is_read_true(db_session, sample_notif):
    notif = sample_notif['N2']

    services.mark_notification_as_read(db_session, notif.id, 3)
    db_session.flush()
    db_session.expire_all()

    db_notif = db_session.get(AdminNotification, notif.id)

    assert db_notif.is_read is True
    assert db_notif.read_staff_id == 3
    assert isinstance(db_notif.read_at, datetime)


def test_mark_notification_as_read__not_found__raises(db_session):
    with pytest.raises(NotFoundError):
        services.mark_notification_as_read(db_session, 999, 1)
