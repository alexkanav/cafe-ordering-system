import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from infrastructure.db.models.users import Dish, DishLike, Category
from domain import services
from domain import schemas
from domain.core.errors import NotFoundError
from tests.factories.dish import make_dish_schema


@pytest.fixture
def sample_menu(db_session):
    cat1 = Category(name="Cat1", order=1)
    cat2 = Category(name="Cat2", order=2)
    db_session.add_all([cat1, cat2])
    db_session.flush()

    dishes = [
        Dish(code="A1", name="n1", price=10, category_id=cat1.id, description="d1", image_link="A1.jpg"),
        Dish(code="A2", name="n2", price=0, category_id=cat1.id, description="d2", image_link="A2.jpg"),
        Dish(code="B1", name="n3", price=15, category_id=cat2.id, description="d3", image_link=None),
        Dish(code="B2", name="n4", price=-5, category_id=cat2.id, description="d4", image_link="B2.jpg"),
    ]

    db_session.add_all(dishes)
    db_session.flush()


def test_update_categories__reordered_categories__updates_category_order(db_session, sample_menu):
    categories = ["cat2", "cat3", "cat1"]

    services.update_categories(db_session, categories)
    db_session.flush()

    db_categories = (
        db_session.query(Category)
        .order_by(Category.order)
        .all()
    )

    assert [(c.name, c.order) for c in db_categories] == [
        ("Cat2", 1),
        ("Cat3", 2),
        ("Cat1", 3),
    ]


def test_create_or_update_dish__dish_does_not_exist__creates_new_dish(db_session):
    dish = make_dish_schema()
    services.create_or_update_dish(db_session, dish)
    db_session.flush()
    db_dish = db_session.get(Dish, dish.code)

    assert db_dish.name == dish.name
    assert db_dish.category_id == dish.category_id
    assert db_dish.description == dish.description
    assert db_dish.price == dish.price
    assert db_dish.image_link == dish.image_link


def test_create_or_update_dish__dish_exists__updates_only_provided_fields(db_session, sample_menu):
    code = "A2"
    price = 120
    dish = make_dish_schema(code=code, price=price, image_link="")

    services.create_or_update_dish(db_session, dish)

    db_session.flush()
    db_dish = db_session.get(Dish, code)

    assert db_dish.name == dish.name
    assert db_dish.category_id == dish.category_id
    assert db_dish.description == dish.description
    assert db_dish.price == price
    assert db_dish.image_link == "A2.jpg"


@pytest.mark.parametrize("include_unpriced, expected_result", [
    (True, {('A1', 10), ('A2', 0), ('B1', 15), ('B2', -5)}),
    (False, {('A1', 10), ('B1', 15)}),
])
def test_get_dishes__include_unpriced__returns_dishes(
        db_session,
        sample_menu,
        include_unpriced,
        expected_result,
):
    response = services.get_dishes(db_session, include_unpriced)
    assert isinstance(response, schemas.GetDishesResponseSchema)

    result = {(code, dish.price) for code, dish in response.dishes.items()}

    assert result == expected_result

    assert response.featured_dishes[0].root == {"Популярне": []}
    assert response.featured_dishes[1].root == {"Рекомендуємо": []}


def test_add_dish_like__dish_exists__creates_like_and_increments_counter(db_session, sample_menu):
    dish_before = db_session.get(Dish, "A1")
    assert dish_before.likes == 0

    services.add_dish_like(db_session, user_id=2, dish_code="A1")

    dish_after = db_session.get(Dish, "A1")
    assert dish_after.likes == 1

    dish_like = db_session.get(DishLike, (2, "A1"))
    assert dish_like.user_id == 2
    assert dish_like.dish_code == "A1"
    assert isinstance(dish_like.created_at, datetime)


def test_add_dish_like__dish_does_not_exist__raises_not_found_error(db_session, sample_menu):
    with pytest.raises(NotFoundError):
        services.add_dish_like(db_session, user_id=2, dish_code="A5")


def test_add_dish_like__like_already_exists__raises_integrity_error(db_session, sample_menu):
    services.add_dish_like(db_session, user_id=2, dish_code="A1")
    dish_like = db_session.get(DishLike, (2, "A1"))
    assert dish_like is not None

    with pytest.raises(IntegrityError):
        services.add_dish_like(db_session, user_id=2, dish_code="A1")


@pytest.mark.parametrize("include_unpriced, expected_categories", [
    (True, [{'Cat1': ['A1', 'A2']}, {'Cat2': ['B1', 'B2']}]),
    (False, [{'Cat1': ['A1']}, {'Cat2': ['B1']}]),
])
def test_get_categories__include_unpriced__returns_categories_with_dishes(
        db_session,
        sample_menu,
        include_unpriced,
        expected_categories,
):
    response = services.get_categories(db_session, include_unpriced)

    assert isinstance(response, schemas.GetCategoriesResponseSchema)

    assert [c.model_dump() for c in response.categories] == expected_categories

    assert response.category_id_map == {"Cat1": 1, "Cat2": 2}


def test_get_categories__no_categories_exist__returns_empty_response(db_session):
    response = services.get_categories(db_session, include_unpriced=True)

    assert response.categories == []
    assert response.category_id_map == {}


def test_build_user_menu__menu_exists__returns_only_priced_dishes(db_session, sample_menu):
    response = services.build_user_menu(db_session)

    assert isinstance(response, schemas.UserMenuResponseSchema)

    assert response.dishes.keys() == {"A1", "B1"}

    dish_a1 = response.dishes["A1"]
    assert dish_a1.name == "n1"
    assert dish_a1.price == 10


def test_build_staff_menu__menu_exists__returns_full_menu_with_categories(db_session, sample_menu):
    response = services.build_staff_menu(db_session)

    assert isinstance(response, schemas.StaffMenuResponseSchema)

    assert response.dishes.keys() == {"A1", "A2", "B1", "B2"}

    dish_a2 = response.dishes["A2"]
    assert dish_a2.name == "n2"
    assert dish_a2.price == 0

    assert response.featured_dishes[0].root == {"Популярне": []}
    assert response.featured_dishes[1].root == {"Рекомендуємо": []}

    assert [c.model_dump() for c in response.categories] == [
        {'Cat1': ['A1', 'A2']},
        {'Cat2': ['B1', 'B2']}
    ]
    assert response.category_id_map == {
        "Cat1": 1,
        "Cat2": 2,
    }
