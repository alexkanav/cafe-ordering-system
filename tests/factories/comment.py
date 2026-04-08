from datetime import datetime

from domain import schemas


def make_comment_schema(**overrides):
    from utils.enums import CommentStatus
    defaults = {
        "id": 4,
        "user_name": "user",
        "created_at": datetime.utcnow(),
        "comment_text": "comment",
        "status": CommentStatus.pending,
    }
    params = {**defaults, **overrides}
    return schemas.CommentSchema(**params)


def make_comment_create_schema(**overrides):
    defaults = {
        "user_name": "user",
        "comment_text": "comment",
    }
    params = {**defaults, **overrides}
    return schemas.CommentCreateSchema(**params)


def make_comment_payload(**overrides):
    return make_comment_create_schema(**overrides).model_dump()
