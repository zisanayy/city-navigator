from sqlalchemy import Column, Integer, String, DateTime, func
from .database import Base

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    date = Column(DateTime, nullable=True)
    location = Column(String, nullable=True)
    url = Column(String, nullable=True)
    source = Column(String, nullable=True)   
    created_at = Column(DateTime, server_default=func.now())
