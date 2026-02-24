from pydantic import BaseModel, RootModel, ConfigDict, field_validator


class DishSchema(BaseModel):
    name: str
    description: str
    price: int
    is_popular: bool
    is_recommended: bool
    image_link: str | None
    likes: int
    extras: dict[str, int]

    model_config = ConfigDict(from_attributes=True)

    @field_validator("extras", mode="before")
    @classmethod
    def convert_extras(cls, value):
        if isinstance(value, list):
            return {extra.name: extra.price for extra in value}
        return value


class CategoryNamesSchema(BaseModel):
    category_names: list[str]


class CodeList(RootModel[dict[str, list[str]]]):
    pass


class GetDishesResponseSchema(BaseModel):
    dishes: dict[str, DishSchema]
    featured_dishes: list[CodeList]


class GetCategoriesResponseSchema(BaseModel):
    categories: list[CodeList]
    category_id_map: dict[str, int]


class StaffMenuResponseSchema(BaseModel):
    dishes: dict[str, DishSchema]
    featured_dishes: list[CodeList]
    categories: list[CodeList]
    category_id_map: dict[str, int]


class FeaturedDishes(BaseModel):
    popular: list[str]
    recommended: list[str]


class DishUpdateSchema(BaseModel):
    code: str
    name: str | None
    category_id: int | None
    description: str | None
    price: int | None
    image_link: str | None


class UserMenuResponseSchema(BaseModel):
    dishes: dict[str, DishSchema]
    categories: list[CodeList]
