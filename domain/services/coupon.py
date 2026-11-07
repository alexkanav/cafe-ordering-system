from datetime import datetime, UTC

from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from domain.core.errors import NotFoundError, ConflictError, DomainValidationError
from domain.schemas import CouponSchema, CouponCreateSchema
from infrastructure.db.models.users import Coupon
from utils.coupons import generate_coupon_code


def create_coupon(db: Session, data: CouponCreateSchema) -> int:
    code = data.code or generate_coupon_code()

    new_coupon = Coupon(
        code=code,
        discount_value=data.discount_value,
        is_active=True,
        expires_at=data.expires_at,
    )

    try:
        db.add(new_coupon)
        db.flush()
    except IntegrityError:
        db.rollback()
        raise ConflictError(f"Купон з кодом: {code} вже існує")

    return new_coupon.id


def get_available_coupons(db: Session) -> list[CouponSchema]:
    today = datetime.now(UTC).date()
    stmt = select(Coupon).where(
        Coupon.is_active.is_(True),
        or_(
            Coupon.expires_at.is_(None),
            Coupon.expires_at >= today
        )
    )
    coupons = db.scalars(stmt).all()
    return [CouponSchema.model_validate(c) for c in coupons]


def deactivate_coupon(db: Session, coupon_id: int) -> None:
    coupon = db.get(Coupon, coupon_id)
    if not coupon:
        raise NotFoundError(f"Купон: {coupon_id} не знайдено")
    if not coupon.is_active:
        raise ConflictError(f"Купон: {coupon_id} вже деактивовано")

    coupon.is_active = False


def check_coupon(db: Session, coupon_code: str) -> int:
    stmt = (
        select(Coupon)
        .where(Coupon.code == coupon_code)
    )
    coupon = db.scalar(stmt)

    if coupon is None:
        raise NotFoundError("Купон не знайдено")

    if not coupon.is_active:
        raise ConflictError("Купон вже використано")

    if coupon.expires_at and datetime.now(UTC).date() > coupon.expires_at:
        raise DomainValidationError("Купон протермінований")

    return coupon.discount_value


def process_coupon(db: Session, coupon_code: str, user_id: int) -> int:
    stmt = (
        select(Coupon)
        .where(Coupon.code == coupon_code)
        .with_for_update()
    )

    coupon = db.scalar(stmt)

    if coupon is None:
        return 0

    today = datetime.now(UTC).date()

    if not coupon.is_active:
        return 0

    if coupon.expires_at and today > coupon.expires_at:
        return 0

    discount_value = coupon.discount_value

    coupon.user_id = user_id
    coupon.used_at = datetime.now(UTC)
    coupon.is_active = False

    db.flush()

    return discount_value
