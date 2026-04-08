import pytest
from datetime import datetime

from domain.core.errors import NotFoundError
from infrastructure.db.models.users import Comment
from utils.enums import CommentStatus
from domain import services
from domain import schemas
from tests.factories.comment import make_comment_create_schema

name = "client_10"
user_id = 10
content = "text 10"


@pytest.fixture
def sample_comments(db_session):
    comment1 = Comment(user_id=1, user_name="name1", comment_text="text1", status=CommentStatus.approved)
    comment2 = Comment(user_id=2, user_name="name2", comment_text="text2", status=CommentStatus.approved)
    comment3 = Comment(user_id=3, user_name="name3", comment_text="text3", status=CommentStatus.approved)
    comment4 = Comment(user_id=4, user_name="name4", comment_text="text4", status=CommentStatus.pending)
    comment5 = Comment(user_id=5, user_name="name5", comment_text="text5", status=CommentStatus.rejected)

    db_session.add_all([comment1, comment2, comment3, comment4, comment5])
    db_session.flush()

    return {
        "c1": comment1,
        "c2": comment2,
        "c3": comment3,
        "c4": comment4,
        "c5": comment5,
    }


def test_create_comment__valid_data__creates_comment_record(db_session):
    comment_id = services.create_comment(
        db_session,
        user_id,
        make_comment_create_schema(user_name=name, comment_text=content)
    )
    db_session.flush()

    db_comment = (
        db_session.query(Comment)
        .filter_by(user_name=name)
        .first()
    )

    assert isinstance(comment_id, int)
    assert db_comment is not None
    assert db_comment.user_id == user_id
    assert db_comment.comment_text == content
    assert db_comment.status == CommentStatus.pending
    assert isinstance(db_comment.created_at, datetime)


@pytest.mark.parametrize("limit, expected_comments", [
    (10, [("name3", "text3"), ("name2", "text2"), ("name1", "text1")]),
    (2, [("name3", "text3"), ("name2", "text2")]),
])
def test_get_comments__comments_exist__returns_comments_sorted_by_id_desc(
        db_session,
        sample_comments,
        limit,
        expected_comments,
):
    response = services.get_comments(db_session, limit)

    assert len(response) == len(expected_comments)

    assert all(isinstance(c, schemas.CommentSchema) for c in response)

    result = [(c.user_name, c.comment_text) for c in response]
    assert result == expected_comments


def test_get_comments__filters_only_approved(db_session, sample_comments):
    response = services.get_comments(db_session, limit=10)

    assert all(c.status == CommentStatus.approved for c in response)


def test_get_comments__no_comments_exist__returns_empty_list(db_session):
    db_session.query(Comment).delete()
    db_session.flush()

    response = services.get_comments(db_session, limit=10)
    assert response == []


def test_update_comment_status__comments_exist__returns_comment(
        db_session,
        sample_comments,
):
    response = services.update_comment_status(
        db_session,
        user_id,
        sample_comments["c4"].id,
        CommentStatus.approved,
    )
    assert response.status == CommentStatus.approved
    assert response.moderator_id == user_id
    assert isinstance(response.moderated_at, datetime)


def test_update_comment_status__comment_not_found__raises_error(db_session):
    with pytest.raises(NotFoundError):
        services.update_comment_status(db_session, user_id, 999, CommentStatus.approved)
