import datetime

from pydantic import BaseModel


class Payments(BaseModel):
    id: int
    created_at: datetime.datetime
    amount: int
    status: bool
    description: str
    user_tg_id: int