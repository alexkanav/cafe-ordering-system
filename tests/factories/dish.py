from domain import schemas


def make_dish_schema(**overrides):
    defaults = {
        "code": "111",
        "name": "Pizza",
        "category_id": 1,
        "description": "Margarita",
        "price": 100,
        "image_link": "100.jpg",
    }
    params = {**defaults, **overrides}
    return schemas.DishUpdateSchema(**params)


def make_dish_payload(**overrides):
    return make_dish_schema(**overrides).model_dump()
