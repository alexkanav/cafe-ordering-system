from datetime import datetime, UTC
from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from domain.core.errors import NotFoundError, ConflictError, DomainValidationError
from domain.schemas import OrderSchema, OrderItemSchema, OrderCreateSchema, OrderOperationResultSchema
from domain.services.coupon import process_coupon
from domain.services.user import get_total_amount
from infrastructure.db.models.users import Dish, DishExtra
from infrastructure.db.models.users import Order
from utils.discounts import calculate_discount
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
    order.completed_at = datetime.now(UTC)


def get_orders_count(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(Order)) or 0


def calculate_original_cost(db: Session, order_details: dict[str, OrderItemSchema]) -> Decimal:
    requested_dishes = {code: item.quantity for code, item in order_details.items()}
    dishes = db.scalars(
        select(Dish).where(Dish.code.in_(requested_dishes))
    ).all()

    if len(requested_dishes) != len(dishes):
        raise NotFoundError("Замовлені страви зараз недоступні")

    requested_additions = {}
    for items in order_details.values():
        for name, addition in items.additions.items():
            requested_additions[name] = requested_additions.get(name, 0) + addition.quantity

    additions = db.scalars(
        select(DishExtra)
        .where(DishExtra.name.in_(requested_additions))
    ).all()

    addition_prices_by_name = {
        addition.name: Decimal(str(addition.price))
        for addition in additions
    }

    if len(requested_additions) != len(addition_prices_by_name):
        raise NotFoundError("Замовлені доповнення зараз недоступні")

    dish_prices_by_code = {
        dish.code: Decimal(str(dish.price))
        for dish in dishes
    }

    dishes_cost = sum(
        quantity * dish_prices_by_code[code]
        for code, quantity in requested_dishes.items()
    )

    additions_cost = sum(
        addition_prices_by_name[name] * requested_additions[name]
        for name in requested_additions
    )

    return dishes_cost + additions_cost


def calculate_loyalty_pct(db: Session, user_id: int) -> int:
    user_total_amount = get_total_amount(db, user_id)

    return calculate_discount(user_total_amount)


def calculate_final_cost(
        original_cost: Decimal,
        loyalty_pct: int,
        coupon_pct: int,
) -> Decimal:
    discount = Decimal(loyalty_pct + coupon_pct) / Decimal("100")

    return (original_cost * (1 - discount)).quantize(Decimal("0.01"))


def create_order(
        db: Session,
        order_data: OrderCreateSchema,
        user_id: int
) -> OrderOperationResultSchema:
    order_details_dict = {
        k: v.model_dump()
        for k, v in order_data.order_details.items()
    }
    original_cost = calculate_original_cost(db, order_data.order_details)
    if original_cost != order_data.original_cost:
        raise DomainValidationError("Невірна вартість замовлення")

    coupon_pct = 0

    if order_data.coupon_code:
        coupon_pct = process_coupon(db, order_data.coupon_code, user_id)
        if coupon_pct != order_data.coupon_pct:
            raise DomainValidationError("Ваш купон недійсний")

    loyalty_pct = calculate_loyalty_pct(db, user_id)
    final_cost = calculate_final_cost(original_cost, loyalty_pct, coupon_pct)

    new_order = Order(
        user_id=user_id,
        table=order_data.table,
        original_cost=original_cost,
        loyalty_pct=loyalty_pct,
        coupon_pct=coupon_pct,
        final_cost=final_cost,
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
