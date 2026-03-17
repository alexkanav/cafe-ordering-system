from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from domain.core.errors import NotFoundError, ConflictError
from infrastructure.db.models.users import Order
from domain.schemas import OrderSchema, OrderCreateSchema, OrderOperationResultSchema
from utils.orders import calculate_order_lead_time


def get_orders(db: Session, only_uncompleted: bool = True) -> list[OrderSchema]:
    stmt = select(Order).order_by(Order.created_at)
    if only_uncompleted:
        stmt = stmt.where(Order.completed_by.is_(None))

    orders = db.scalars(stmt).all()

    return [OrderSchema.model_validate(order) for order in orders]


def complete_order(db: Session, order_id: int, employee_id: int) -> None:
    order = db.get(Order, order_id)
    if not order:
        raise NotFoundError("Замовлення не знайдено")
    if order.completed_by is not None:
        raise ConflictError("Замовлення вже виконано")

    order.completed_by = employee_id
    order.completed_at = datetime.utcnow()

def get_orders_count(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(Order)) or 0


def create_order(
    db: Session,
    order_data: OrderCreateSchema,
    user_id: int
) -> OrderOperationResultSchema:
    order_details_dict = {
        k: v.model_dump()
        for k, v in order_data.order_details.items()
    }

    new_order = Order(
        user_id=user_id,
        table=order_data.table,
        original_cost=order_data.original_cost,
        loyalty_pct=order_data.loyalty_pct,
        coupon_pct=order_data.coupon_pct,
        final_cost=order_data.final_cost,
        order_details=order_details_dict,
    )
    db.add(new_order)
    db.flush()

    lead_time = calculate_order_lead_time(order_details_dict.keys())

    return OrderOperationResultSchema(
        message="Замовлення прийнято",
        id=new_order.id,
        leadTime=lead_time
    )

