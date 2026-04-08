from domain import schemas


def make_coupon_schema(**overrides):
    defaults = {
        "code": "TEST10",
        "discount_value": 5,
        "expires_at": "2025-10-30",
    }
    params = {**defaults, **overrides}
    return schemas.CouponCreateSchema(**params)


def make_coupon_payload(**overrides):
    return make_coupon_schema(**overrides).model_dump(mode="json")
