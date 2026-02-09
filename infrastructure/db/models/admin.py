from datetime import datetime, date
from sqlalchemy import ForeignKey, Enum, DateTime, Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from utils.enums import NotificationType
from infrastructure.db.base import Base


class Staff(Base):
    __tablename__ = 'staff'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(200))

    created_notifications: Mapped[list["AdminNotification"]] = relationship(
        back_populates="created_by",
        foreign_keys="AdminNotification.created_staff_id",
        cascade="all, delete-orphan"
    )

    read_notifications: Mapped[list["AdminNotification"]] = relationship(
        back_populates="read_by",
        foreign_keys="AdminNotification.read_staff_id",
        cascade="all, delete-orphan"
    )

    orders: Mapped[list["Order"]] = relationship("Order", back_populates="staff")

    @property
    def password(self):
        raise AttributeError("Password is write-only.")

    @password.setter
    def password(self, password_hash: str):
        self.password_hash = password_hash

    def __repr__(self):
        return f"<Staff {self.id}>"


class AdminNotification(Base):
    __tablename__ = "admin_notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50))
    message: Mapped[str] = mapped_column(String(300))
    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType), default=NotificationType.info
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    created_staff_id: Mapped[int | None] = mapped_column(
        ForeignKey("staff.id"),
        nullable=True
    )

    is_read: Mapped[bool] = mapped_column(default=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    read_staff_id: Mapped[int | None] = mapped_column(
        ForeignKey("staff.id"),
        nullable=True
    )
    created_by: Mapped["Staff"] = relationship(
        back_populates="created_notifications",
        foreign_keys=[created_staff_id]
    )

    read_by: Mapped["Staff"] = relationship(
        back_populates="read_notifications",
        foreign_keys=[read_staff_id]
    )

    def __repr__(self):
        return f"<AdminNotification {self.id} title={self.title!r}>"


class SalesSummary(Base):
    __tablename__ = 'sales_summary'

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, unique=True)
    total_sales: Mapped[float]
    orders: Mapped[int]
    returning_customers: Mapped[int]

    def __repr__(self):
        return f"<Sales_summary {self.date}>"


class DishOrdersStats(Base):
    __tablename__ = 'dish_orders_stats'

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(10), unique=True)
    orders: Mapped[int]

    def __repr__(self):
        return f"<Dishes_orders_stats {self.code}>"
