import datetime

from pydantic import BaseModel


class Connection(BaseModel):
    user_id: int
    tg_id: str
    active: bool
    start_date: datetime.datetime | None
    expire_date: datetime.datetime | None
    is_trial: bool
    email: str
    key: str
    description: str

