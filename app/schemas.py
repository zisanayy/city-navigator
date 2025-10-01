from pydantic import BaseModel
from datetime import datetime



class EventBase(BaseModel):
    title: str
    date: datetime | None = None
    location: str | None = None
    url: str | None = None
    source: str | None = None   

class EventCreate(EventBase):
    pass

class EventOut(EventBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True


