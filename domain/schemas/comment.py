from datetime import datetime
from pydantic import BaseModel, ConfigDict, computed_field
from utils.enums import CommentStatus


class CommentSchema(BaseModel):
    id: int
    user_name: str
    created_at: datetime
    comment_text: str
    status: CommentStatus

    @computed_field
    @property
    def comment_date(self) -> str:
        return self.created_at.strftime("%d-%m-%Y")

    model_config = ConfigDict(from_attributes=True)


class CommentCreateSchema(BaseModel):
    user_name: str
    comment_text: str


class CommentResponseSchema(BaseModel):
    comments: list[CommentSchema]


class CommentStatusUpdate(BaseModel):
    status: CommentStatus
