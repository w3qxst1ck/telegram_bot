import datetime

from pydantic import BaseModel


class Connection(BaseModel):
    tg_id: str
    active: bool
    start_date: datetime.datetime | None
    expire_date: datetime.datetime | None
    is_trial: bool
