from sqlalchemy import select, func
from sqlalchemy.orm import Session

from domain.schemas import RegisterRequestSchema, LoginRequestSchema
from domain.core.security import hash_password, verify_password
from infrastructure.db.models.admin import Staff
from infrastructure.db.models.users import User, Order
from infrastructure.db.role_maps import ROLE_MODEL_MAP
from utils.enums import UserRole


def register_staff(db: Session, data: RegisterRequestSchema) -> int:
    user = Staff(
        name=data.username,
        email=data.email,
        password=hash_password(data.password)
    )
    db.add(user)
    db.flush()
    return user.id


def authenticate_staff(db: Session, data: LoginRequestSchema) -> Staff | None:
    user = db.scalar(select(Staff).where(Staff.email == data.email))
    if user and verify_password(data.password, user.password_hash):
        return user
    return None


def get_user_sessions_count(db: Session, user_id: int) -> int:
    stmt = select(func.count(Order.id)).filter_by(user_id=user_id)
    return db.scalar(stmt) or 0


def create_user(db: Session) -> int:
    user = User()
    db.add(user)
    db.flush()
    return user.id


def get_total_amount(db: Session, user_id: int) -> int:
    stmt = select(func.sum(Order.final_cost)).filter_by(user_id=user_id)
    return db.scalar(stmt) or 0


def user_exists_for_role(db: Session, user_id: int, role: UserRole) -> bool:
    return db.get(ROLE_MODEL_MAP[role], user_id) is not None
