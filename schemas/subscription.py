import datetime

from pydantic import BaseModel


class Subscription(BaseModel):
    id: int
    active: bool
    created_at: datetime.datetime | None
    expired_at: datetime.datetime | None