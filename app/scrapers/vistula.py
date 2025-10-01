import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser
from typing import Iterator, Dict, Optional
from datetime import datetime

VISTULA_NEWS = "https://vistula.edu.pl/en/news"

def fetch_vistula_events() -> Iterator[Dict]:
    html = requests.get(VISTULA_NEWS, timeout=20).text
    soup = BeautifulSoup(html, "html.parser")

    # Haber/etkinlik kartlarını yakala (WordPress benzeri)
    # Farklı temalara dayanıklı olması için birkaç seçici:
    cards = soup.select("article, .post, .news-item, .et_pb_post, .entry")
    for el in cards:
        a = el.select_one("h2 a[href], a[href]")
        if not a:
            continue
        title = a.get_text(strip=True)
        link = a["href"]

        # tarih bul
        dt: Optional[datetime] = None
        t = el.select_one("time[datetime]") or el.select_one("time")
        date_txt = None
        if t:
            date_txt = t.get("datetime") or t.get_text(" ", strip=True)
        else:
            d = el.select_one(".date, .published, .entry-date")
            if d:
                date_txt = d.get_text(" ", strip=True)

        try:
            dt = dateparser.parse(date_txt, dayfirst=True, fuzzy=True) if date_txt else None
        except Exception:
            dt = None

        # bazen etkinlik gerçek detay sayfasında net bilgiler olur—linki de kaydediyoruz
        yield {
            "title": title,
            "url": link,
            "date": dt,
            "location": "Vistula University",
            "source": "vistula_news",
        }
