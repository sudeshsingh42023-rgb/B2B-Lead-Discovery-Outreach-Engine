"""Visit each lead's website and extract digital-gap signals.

Only reads public pages (one GET per site). Be polite: small batches, a delay between requests.
"""
import re
import time
from datetime import date

import pandas as pd
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (lead-research; contact: your-email)"}
BOOKING_WORDS = ("book now", "book online", "book appointment", "add to cart",
                 "checkout", "order online", "schedule a", "buy now")


def inspect_site(url: str, timeout: int = 10) -> dict:
    out = {"site_ok": 0, "load_s": None, "https": 0, "mobile_friendly": 0,
           "online_booking": 0, "whatsapp_link": 0, "app_link": 0,
           "copyright_year": None}
    if not isinstance(url, str) or not url.strip():
        return out
    if not url.startswith("http"):
        url = "https://" + url
    try:
        t0 = time.time()
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        out["load_s"] = round(time.time() - t0, 2)
        out["site_ok"] = int(r.status_code < 400)
        out["https"] = int(r.url.startswith("https"))
        html = r.text
        soup = BeautifulSoup(html, "html.parser")
        out["mobile_friendly"] = int(bool(soup.find("meta", attrs={"name": "viewport"})))
        low = html.lower()
        out["online_booking"] = int(any(w in low for w in BOOKING_WORDS))
        out["whatsapp_link"] = int("wa.me" in low or "api.whatsapp.com" in low)
        out["app_link"] = int("play.google.com/store" in low or "apps.apple.com" in low)
        years = [int(y) for y in re.findall(r"(?:©|&copy;|copyright)[^0-9]{0,20}((?:19|20)\d{2})", low)]
        out["copyright_year"] = max(years) if years else None
    except requests.RequestException:
        pass
    return out


def enrich(df: pd.DataFrame, delay: float = 1.0) -> pd.DataFrame:
    rows = []
    for _, lead in df.iterrows():
        rows.append(inspect_site(lead.get("website")))
        time.sleep(delay)
    return pd.concat([df.reset_index(drop=True), pd.DataFrame(rows)], axis=1)


def is_outdated(copyright_year) -> bool:
    try:
        return int(copyright_year) < date.today().year - 2
    except (TypeError, ValueError):
        return False
