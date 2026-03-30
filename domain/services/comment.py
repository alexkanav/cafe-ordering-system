from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.schemas import CommentSchema, CommentCreateSchema
from infrastructure.db.models.users import Comment
from utils.enums import CommentStatus
from domain.core.errors import NotFoundError
from utils.notification import notify_moderator


def get_comments(db: Session, limit: int) -> list[CommentSchema]:
    stmt = (
        select(Comment)
        .where(Comment.status == CommentStatus.approved)
        .order_by(Comment.id.desc())
        .limit(limit)
    )

    comments = db.scalars(stmt).all()
    return [CommentSchema.model_validate(c) for c in comments]


def create_comment(db: Session, user_id: int, data: CommentCreateSchema, notifier=notify_moderator) -> int:
    comment = Comment(
        user_id=user_id,
        user_name=data.user_name,
        comment_text=data.comment_text,
        status=CommentStatus.pending,
    )
    db.add(comment)
    db.flush()

    notifier(comment.id)

    return comment.id


def update_comment_status(db: Session, user_id: int, comment_id: int, new_status: CommentStatus) -> Comment:
    comment = db.get(Comment, comment_id)
    if not comment:
        raise NotFoundError(f"Коментар {comment_id} не знайдено")

    comment.status = new_status
    comment.moderator_id = user_id
    comment.moderated_at = datetime.utcnow()
    db.flush()

    return comment
