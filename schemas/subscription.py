import datetime

from pydantic import BaseModel


class Subscription(BaseModel):
    id: int
    active: bool
    created_at: datetime.datetime
    start_date: datetime.datetime | None
    expire_date: datetime.datetime | None

