from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .. import models, schemas, database
from run_scrapers import scrape_all

router = APIRouter(prefix="/events", tags=["events"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[schemas.EventOut])
def list_events(
    q: str | None = None,
    source: str | None = None,
    future_only: bool = True,
    limit: int = 100,
    date_from: str | None = None,   
    date_to: str | None = None,     
    db: Session = Depends(get_db),
):
    query = db.query(models.Event)

    if q:
        like = f"%{q}%"
        query = query.filter(models.Event.title.ilike(like))

    if source:
        query = query.filter(models.Event.source == source)

    if date_from:
        try:
            df = datetime.fromisoformat(date_from)
            query = query.filter(models.Event.date != None, models.Event.date >= df)  
        except Exception:
            pass
    if date_to:
        try:
            dt = datetime.fromisoformat(date_to)
            query = query.filter(models.Event.date != None, models.Event.date <= dt)  
        except Exception:
            pass

    if future_only and not (date_from or date_to):
        now = datetime.now()
        query = query.filter((models.Event.date == None) | (models.Event.date >= now))  

    query = query.order_by(models.Event.date.is_(None), models.Event.date.asc())

    return query.limit(min(limit, 500)).all()

@router.get("/today", response_model=list[schemas.EventOut])
def events_today(db: Session = Depends(get_db)):
    now = datetime.now()
    start = datetime(now.year, now.month, now.day)
    end = start + timedelta(days=1)
    q = (db.query(models.Event)
           .filter((models.Event.date != None) & (models.Event.date >= start) & (models.Event.date < end)) 
           .order_by(models.Event.date.asc()))
    return q.all()

@router.get("/this_week", response_model=list[schemas.EventOut])
def events_this_week(db: Session = Depends(get_db)):
    now = datetime.now()
    start = datetime(now.year, now.month, now.day)
    end = start + timedelta(days=7)
    q = (db.query(models.Event)
           .filter((models.Event.date != None) & (models.Event.date >= start) & (models.Event.date < end))  
           .order_by(models.Event.date.asc()))
    return q.all()

@router.post("/refresh", tags=["admin"])
def refresh_events(db: Session = Depends(get_db)):
    """Manuel scraping tetikler."""
    msg = scrape_all()
    return {"ok": True, "message": msg}
