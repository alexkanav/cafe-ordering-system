from domain import schemas


def make_order_details_schema(**overrides):
    defaults = {
        "name": "Pizza",
        "quantity": 2,
        "price": 200,
        "additions": {"cheese": 20},
    }

    params = {**defaults, **overrides}

    return schemas.OrderItemSchema(**params)


def make_order_schema(**overrides):
    defaults = {
        "table": 8,
        "original_cost": 200,
        "loyalty_pct": 10,
        "coupon_pct": 5,
        "final_cost": 170,
        "order_details": {"125": make_order_details_schema()}
    }

    params = {**defaults, **overrides}
    return schemas.OrderCreateSchema(**params)


def make_order_payload(**overrides):
    return make_order_schema(**overrides).model_dump()


def make_order_operation_result_schema(**overrides):
    defaults = {
        "message": "Замовлення прийнято",
        "id": 3,
        "leadTime": 30,
    }

    params = {**defaults, **overrides}
    return schemas.OrderOperationResultSchema(**params)
