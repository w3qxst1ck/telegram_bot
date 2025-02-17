import datetime

from pydantic import BaseModel


class Subscription(BaseModel):
    tg_id: str
    active: bool
    # created_at: datetime.datetime
    start_date: datetime.datetime | None
    expire_date: datetime.datetime | None
    is_trial: bool
    trial_used: bool

