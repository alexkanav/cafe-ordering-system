from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


class OrderItemSchema(BaseModel):
    name: str
    quantity: int
    price: int
    additions: dict[str, int] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class OrderSchema(BaseModel):
    id: int
    table: int | None
    order_details: dict[str, OrderItemSchema]
    original_cost: Decimal
    loyalty_pct: int = 0
    coupon_pct: int = 0
    final_cost: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderCreateSchema(BaseModel):
    table: int
    original_cost: Decimal
    loyalty_pct: int = 0
    coupon_pct: int = 0
    final_cost: Decimal
    order_details: dict[str, OrderItemSchema]
    coupon_code: str = ""

    model_config = ConfigDict(from_attributes=True)


class OrderOperationResultSchema(BaseModel):
    message: str
    id: int
    leadTime: int


class OrderResponseSchema(BaseModel):
    orders: list[OrderSchema]
    orders_count: int


class OrderCountResponseSchema(BaseModel):
    count: int
