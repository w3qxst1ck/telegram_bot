import datetime

from pydantic import BaseModel
from schemas.subscription import Subscription


class UserAdd(BaseModel):
    tg_id: str
    username: str | None
    firstname: str | None
    lastname: str | None


class User(UserAdd):
    id: int
    created_at: datetime.datetime


class UserSubscription(User, Subscription):
    pass

