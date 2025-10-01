# run_scrapers.py
from app.database import SessionLocal
from app.models import Event
from app.scrapers.warsaw import fetch_warsaw_events
from app.scrapers.vistula import fetch_vistula_events

def save_events(items, db):
    added = 0
    for e in items:
        title = e.get("title")
        url = e.get("url")
        date = e.get("date")
        location = e.get("location")
        source = e.get("source")

        if not title:
            continue

        q = db.query(Event).filter(Event.title == title)
        if url:    q = q.filter(Event.url == url)
        if source: q = q.filter(Event.source == source)
        if q.first():
            continue

        db.add(Event(
            title=title,
            date=date,
            location=location,
            url=url,
            source=source
        ))
        added += 1
    db.commit()
    return added

def scrape_all():
    db = SessionLocal()
    try:
        n1 = save_events(fetch_warsaw_events(), db)
        n2 = save_events(fetch_vistula_events(), db)
        return f"Scraping finished, added {n1+n2} events (UW:{n1}, Vistula:{n2})."
    finally:
        db.close()

if __name__ == "__main__":
    print(scrape_all())
