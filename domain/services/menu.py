from sqlalchemy import select, update as sa_update
from sqlalchemy.orm import selectinload, Session, with_loader_criteria

from domain.core.errors import NotFoundError
from infrastructure.db.models.users import Category, Dish, DishLike
from domain import schemas


def update_categories(db: Session, categories: list[str]) -> None:
    """
    order_list: list of category names in the desired order.
    If a category name doesn't exist, it will be created.
    """
    categories = [c.strip().title() for c in categories]
    existing_names = {
        name for (name,) in db.execute(select(Category.name)).all()
    }
    for order, name in enumerate(categories, start=1):
        if name in existing_names:
            db.execute(
                (
                    sa_update(Category)
                    .where(Category.name == name)
                    .values(order=order)

                )
            )
        else:
            # Create new category if not found
            db.add(Category(name=name, order=order))


def create_or_update_dish(db: Session, dish_data: schemas.DishUpdateSchema) -> None:
    dish = db.get(Dish, dish_data.code)

    price = int(dish_data.price or 0)

    if dish:
        if dish_data.name:
            dish.name = dish_data.name

        if dish_data.description:
            dish.description = dish_data.description

        if dish_data.image_link:
            dish.image_link = dish_data.image_link

        if dish_data.category_id:
            dish.category_id = dish_data.category_id

        dish.price = price

    else:
        dish = Dish(
            code=dish_data.code,
            name=dish_data.name,
            category_id=dish_data.category_id,
            description=dish_data.description,
            price=price,
            image_link=dish_data.image_link or None,
        )
        db.add(dish)


def add_dish_like(db: Session, user_id: int, dish_code: str) -> None:
    dish = db.scalar(
        select(Dish)
        .where(Dish.code == dish_code)
        .with_for_update()
    )

    if not dish:
        raise NotFoundError("Страву не знайдено")

    db.add(DishLike(user_id=user_id, dish_code=dish_code))
    db.flush()

    dish.likes += 1


def get_dishes(db: Session, include_unpriced: bool) -> schemas.GetDishesResponseSchema:
    dish_query = select(Dish)
    if not include_unpriced:
        dish_query = dish_query.where(Dish.price > 0)

    dish_list = db.scalars(dish_query).all()

    dishes: dict[str, schemas.DishSchema] = {}
    popular: list[str] = []
    recommended: list[str] = []

    for dish in dish_list:
        dishes[dish.code] = schemas.DishSchema.model_validate(dish)
        if dish.is_popular:
            popular.append(dish.code)
        if dish.is_recommended:
            recommended.append(dish.code)

    featured_dishes = [{"Популярне": popular}, {"Рекомендуємо": recommended}]

    return schemas.GetDishesResponseSchema(dishes=dishes, featured_dishes=featured_dishes)


def get_categories(db: Session, include_unpriced: bool) -> schemas.GetCategoriesResponseSchema:
    query = select(Category).order_by(Category.order)

    if not include_unpriced:
        query = query.options(
            selectinload(Category.dishes),
            with_loader_criteria(Dish, Dish.price > 0),
        )
    else:
        query = query.options(selectinload(Category.dishes))

    category_list = db.scalars(query).all()

    categories = [
        {
            category.name: [dish.code for dish in category.dishes]
        }
        for category in category_list
    ]
    category_id_map = {cat.name: cat.id for cat in category_list}

    return schemas.GetCategoriesResponseSchema(categories=categories, category_id_map=category_id_map)


def build_user_menu(db: Session) -> schemas.UserMenuResponseSchema:
    dish_result = get_dishes(db, include_unpriced=False)
    category_result = get_categories(db, include_unpriced=False)

    categories = category_result.categories + dish_result.featured_dishes

    return schemas.UserMenuResponseSchema(
        dishes=dish_result.dishes,
        categories=categories
    )


def build_staff_menu(db: Session) -> schemas.StaffMenuResponseSchema:
    dish_data = get_dishes(db, include_unpriced=True)
    categories_data = get_categories(db, include_unpriced=True)

    return schemas.StaffMenuResponseSchema(
        dishes=dish_data.dishes,
        featured_dishes=dish_data.featured_dishes,
        categories=categories_data.categories,
        category_id_map=categories_data.category_id_map
    )
