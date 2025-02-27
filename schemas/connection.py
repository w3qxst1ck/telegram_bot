import datetime

from pydantic import BaseModel


class Connection(BaseModel):
    tg_id: str
    active: bool
    start_date: datetime.datetime | None
    expire_date: datetime.datetime | None
    is_trial: bool
    email: str
    key: str
    description: str
    server_id: int



class ServerAdd(BaseModel):
    name: str
    region: str
    api_url: str
    domain: str
    inbound_id: int


class Server(ServerAdd):
    id: int
