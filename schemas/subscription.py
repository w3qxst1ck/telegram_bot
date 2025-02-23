import datetime

from pydantic import BaseModel


class Subscription(BaseModel):
    tg_id: str
    active: bool
    start_date: datetime.datetime | None
    expire_date: datetime.datetime | None
    is_trial: bool
    trial_used: bool
    balance: int
