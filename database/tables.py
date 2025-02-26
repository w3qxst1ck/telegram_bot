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
    balance: Mapped[int] = mapped_column(default=0)
    trial_used: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=text("TIMEZONE('utc-3', now())"))

    payments: Mapped[list["Payment"]] = relationship(back_populates="user")

    connections: Mapped[list["Connection"]] = relationship(back_populates="user")


class Connection(Base):
    """Подключения"""
    __tablename__ = "connections"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[str] = mapped_column(ForeignKey("users.tg_id", ondelete="CASCADE"))
    active: Mapped[bool] = mapped_column(default=False)
    start_date: Mapped[datetime.datetime] = mapped_column(nullable=True, default=None)
    expire_date: Mapped[datetime.datetime] = mapped_column(nullable=True, default=None)
    is_trial: Mapped[bool] = mapped_column(default=True)
    email: Mapped[str] = mapped_column(index=True, unique=True)
    key: Mapped[str]
    description: Mapped[str]

    # user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="connections")

    server_id: Mapped[int] = mapped_column(ForeignKey("servers.id", ondelete="CASCADE"))
    server: Mapped["Server"] = relationship(back_populates="connections")


class Payment(Base):
    """Платежи"""
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime.datetime]
    amount: Mapped[int]
    status: Mapped[bool] = mapped_column(default=False)

    user_tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="payments")


class Server(Base):
    """Сервера с vpn"""
    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    region: Mapped[str]
    api_url: Mapped[str]
    domain: Mapped[str]
    inbound_id: Mapped[int] = mapped_column(default=1)

    connections: Mapped[list["Connection"]] = relationship(
        back_populates="server",
    )

