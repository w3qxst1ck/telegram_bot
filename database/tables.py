import datetime

from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy import text, ForeignKey


class Base(DeclarativeBase):
    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"


class User(Base):
    """Пользователи"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[str] = mapped_column(index=True, unique=True)
    username: Mapped[str] = mapped_column(nullable=True)
    firstname: Mapped[str] = mapped_column(nullable=True)
    lastname: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))

    payments: Mapped[list["Payment"]] = relationship(
        back_populates="user",
    )


class TestSubscription(Base):
    """Тестовые разовые подписки"""
    __tablename__ = "test_subscriptions"

    tg_id: Mapped[str] = mapped_column(primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc-3', now())")
    )
    expired_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc-3', now() + interval '1 day')")
    )


class Subscription(Base):
    """Подписки"""
    __tablename__ = "subscriptions"

    tg_id: Mapped[str] = mapped_column(primary_key=True)
    created_at: Mapped[datetime.datetime]
    expired_at: Mapped[datetime.datetime]


class Payment(Base):
    """Платежи"""
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime.datetime]
    amount: Mapped[int]
    status: Mapped[bool] = mapped_column(default=False)

    user_tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="payments")


