from pydantic import BaseModel


class Referrals(BaseModel):
    id: int
    from_user_id: str
    to_user_id: str
    is_used: bool

