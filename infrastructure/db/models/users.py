from datetime import datetime, date
from sqlalchemy import Table, Column, ForeignKey, DateTime, Date, String, Integer, JSON, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.db.base import Base

dish_extra_link = Table(
    "dish_extra_link",
    Base.metadata,
    Column("dish_id", ForeignKey("dishes.code"), primary_key=True),
    Column("extra_id", ForeignKey("dish_extras.id"), primary_key=True),
)


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    orders: Mapped[list["Order"]] = relationship(back_populates="user")
    comments: Mapped[list["Comment"]] = relationship(back_populates="user")
    coupons: Mapped[list["Coupon"]] = relationship(back_populates="user")
    like_rel: Mapped[list["DishLike"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User {self.id}>"


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    order: Mapped[int] = mapped_column(default=0)

    dishes: Mapped[list["Dish"]] = relationship(back_populates="category")

    def __repr__(self) -> str:
        return f"<Category {self.name}>"


class Dish(Base):
    __tablename__ = 'dishes'

    code: Mapped[str] = mapped_column(String(4), primary_key=True)
    name_en: Mapped[str] = mapped_column(String(30))
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    is_popular: Mapped[bool] = mapped_column(default=False, index=True)
    is_recommended: Mapped[bool] = mapped_column(default=False, index=True)
    name: Mapped[str] = mapped_column(String(50))
    price: Mapped[int] = mapped_column(default=0)
    description: Mapped[str] = mapped_column(String(500))
    image_link: Mapped[str | None] = mapped_column(String(50), nullable=True)
    views: Mapped[int] = mapped_column(default=0)
    likes: Mapped[int] = mapped_column(default=0)

    category: Mapped["Category"] = relationship(back_populates="dishes")
    like_rel: Mapped[list["DishLike"]] = relationship(back_populates="dish", cascade="all, delete-orphan")
    extras: Mapped[list["DishExtra"]] = relationship(
        "DishExtra",
        secondary=dish_extra_link,
        back_populates="dishes"
    )

    def __repr__(self) -> str:
        return f"<Dish {self.code} name={self.name}>"


class DishLike(Base):
    __tablename__ = "dish_likes"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    dish_code: Mapped[str] = mapped_column(ForeignKey("dishes.code"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="like_rel")
    dish: Mapped["Dish"] = relationship(back_populates="like_rel")

    def __repr__(self) -> str:
        return f"<DishLike user_id={self.user_id} dish_code={self.dish_code}>"


class DishExtra(Base):
    __tablename__ = 'dish_extras'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), unique=True)
    name_ua: Mapped[str] = mapped_column(String(20))
    price: Mapped[float] = mapped_column(Numeric(10, 2), default=0)

    dishes: Mapped[list["Dish"]] = relationship(
        "Dish",
        secondary=dish_extra_link,
        back_populates="extras"
    )

    def __repr__(self) -> str:
        return f"<DishExtra {self.name}>"


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_by: Mapped[int | None] = mapped_column(
        ForeignKey("staff.id"),
        nullable=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    table: Mapped[int | None] = mapped_column(nullable=True)
    original_cost: Mapped[float] = mapped_column(Numeric(10, 2))
    loyalty_pct: Mapped[int] = mapped_column(default=0)
    coupon_pct: Mapped[int] = mapped_column(default=0)
    final_cost: Mapped[float] = mapped_column(Numeric(10, 2))
    order_details: Mapped[dict] = mapped_column(JSON)

    user: Mapped["User"] = relationship(back_populates="orders")
    staff: Mapped["Staff"] = relationship("Staff", back_populates="orders")

    def __repr__(self) -> str:
        return f"<Order {self.id}>"


class Comment(Base):
    __tablename__ = 'comments'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user_name: Mapped[str] = mapped_column(String(20))
    comment_date_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    comment_text: Mapped[str] = mapped_column(String(200))

    user: Mapped["User"] = relationship(back_populates="comments")

    def __repr__(self) -> str:
        return f"<Comment {self.id}>"


class Coupon(Base):
    __tablename__ = 'coupons'

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True)
    discount_value: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    expires_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    user: Mapped['User'] = relationship('User', back_populates='coupons')

    def __repr__(self) -> str:
        return f"<Coupon {self.code}>"
