import datetime
from typing import List

from pydantic import BaseModel
from schemas.connection import Connection


class UserAdd(BaseModel):
    tg_id: str
    username: str | None
    firstname: str | None
    lastname: str | None
    balance: int
    trial_used: bool


class User(UserAdd):
    id: int
    created_at: datetime.datetime


class UserConnection(User, Connection):
    pass


class UserConnList(User):
    connections: List[Connection]

