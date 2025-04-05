import datetime

from pydantic import BaseModel


class ServerAdd(BaseModel):
    name: str
    region: str
    api_url: str
    domain: str
    inbound_id: int


class Server(ServerAdd):
    id: int


class Connection(BaseModel):
    tg_id: str
    active: bool
    start_date: datetime.datetime | None
    expire_date: datetime.datetime | None
    is_trial: bool
    email: str
    key: str
    description: str | None
    server_id: int
    traffic: float | None = None


class ConnectionRegion(BaseModel):
    id: int
    description: str
    region: str


class ConnServerScheduler(BaseModel):
    tg_id: str
    email: str
    description: str
    api_url: str
    inbound_id: int


class ConnectionServer(Connection, ServerAdd):
    pass




