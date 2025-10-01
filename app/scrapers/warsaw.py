# app/scrapers/warsaw.py
import re
import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser
from datetime import datetime
from typing import Iterator, Dict, Optional

UPCOMING_URL = "https://welcome.uw.edu.pl/upcoming-events/"

YEAR_PAT = re.compile(r"\b(19|20)\d{2}\b", re.I)  # metinde yıl var mı?

def normalize_year(dt: Optional[datetime], raw_text: str) -> Optional[datetime]:
    """
    1) Metinde yıl yoksa -> bu yıl
    2) Bu yıl ile sonuç geçmişe düşüyorsa -> gelecek yıl (gelecekteki en yakın tarih)
    3) Aykırı 2007 gibi geçmiş yıllar gelirse -> bu yıl (ve yine geleceğe çek)
    """
    if dt is None:
        return None

    now = datetime.now()
    has_explicit_year = bool(YEAR_PAT.search(raw_text))

    # Eğer parser anlamsız geçmiş bir yıl yakaladıysa (örn. 2007), yıl işini biz devralalım
    if (not has_explicit_year) or (dt.year < now.year - 1):
        dt = dt.replace(year=now.year)

    # Yıl yoktu ve bu yıl ile tarih geçmişe düştü -> bir sonraki yıl yap
    if dt.date() < now.date() and not has_explicit_year:
        dt = dt.replace(year=now.year + 1)

    return dt

def fetch_warsaw_events() -> Iterator[Dict]:
    html = requests.get(UPCOMING_URL, timeout=20).text
    soup = BeautifulSoup(html, "html.parser")

    # H2/H3 başlıklarının altındaki listeleri tara
    sections = soup.select("h2, h3")
    seen = set()

    for h in sections:
        # doğrudan kardeşinde ul/ol, yoksa bir div içinde
        ul = h.find_next_sibling(lambda tag: tag.name in ["ul", "ol"])
        if not ul:
            wrap = h.find_next_sibling("div")
            if wrap:
                ul = wrap.find("ul") or wrap.find("ol")
        if not ul:
            continue

        for li in ul.select("li"):
            text = li.get_text(" ", strip=True)
            if not text:
                continue

            # basit tekrar koruması
            key = (text, UPCOMING_URL)
            if key in seen:
                continue
            seen.add(key)

            # link
            a = li.find("a", href=True)
            url = a["href"] if a else UPCOMING_URL

            # tarih parse
            dt: Optional[datetime] = None
            try:
                # default'ı bu yılın başı yapıyoruz (yıl verilmemişse bu yıl kullansın)
                default_base = datetime(datetime.now().year, 1, 1)
                dt = dateparser.parse(text, dayfirst=False, fuzzy=True, default=default_base)
            except Exception:
                dt = None

            dt = normalize_year(dt, text)

            # başlık -> "Welcome Meeting – Oct 24" -> "Welcome Meeting"
            title = text.split(" – ")[0].strip()

            yield {
                "title": title,
                "url": url,
                "date": dt,
                "location": "University of Warsaw",
                "source": "uw_welcome_point",
            }
