from enum import Enum


class NotificationType(str, Enum):
    info = "info"
    warning = "warning"
    urgent = "urgent"
    success = "success"


class UserRole(str, Enum):
    client = "client"
    staff = "staff"
    moderator = "moderator"
    admin = "admin"


class CommentStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
