"""Score leads 0-100 on 'how likely do they need custom software' and assign a service fit."""
import pandas as pd

from .config import CONSUMER_INDUSTRIES, WEIGHTS
from .enrich import is_outdated


def _flag(v):
    """Return True/False/None from 1/0/yes/no/blank."""
    if pd.isna(v) or str(v).strip() == "":
        return None
    return str(v).strip().lower() in {"1", "1.0", "true", "yes", "y"}


def website_gap_points(r):
    website = r.get("website")
    if pd.isna(website) or str(website).strip() == "":
        return float(WEIGHTS["website_gap"]), ["no website"]
    if "site_ok" not in r or pd.isna(r.get("site_ok")):
        return 0.0, []                      # not enriched: no evidence of a gap
    checks = []
    if not r["site_ok"]:
        checks.append("site unreachable")
    if pd.notna(r.get("load_s")) and float(r["load_s"]) > 3:
        checks.append("slow load")
    if not r.get("https"):
        checks.append("no HTTPS")
    if not r.get("mobile_friendly"):
        checks.append("not mobile friendly")
    if is_outdated(r.get("copyright_year")):
        checks.append("outdated site")
    return len(checks) / 5 * WEIGHTS["website_gap"], checks


def score_lead(r) -> pd.Series:
    pts, reasons = 0.0, []

    p, rs = website_gap_points(r)
    pts += p
    reasons += rs

    industry = str(r.get("industry", "")).strip().lower()
    app = _flag(r.get("has_mobile_app"))
    if app is None and pd.notna(r.get("app_link")):
        app = bool(r["app_link"])
    no_app = (app is False) and industry in CONSUMER_INDUSTRIES
    if no_app:
        pts += WEIGHTS["no_app"]
        reasons.append("no mobile app")

    manual = _flag(r.get("manual_workflow"))
    if manual is None and pd.notna(r.get("whatsapp_link")):
        manual = bool(r["whatsapp_link"]) and not bool(r.get("online_booking"))
    if manual:
        pts += WEIGHTS["manual_workflow"]
        reasons.append("manual WhatsApp/phone workflow")

    try:
        size = int(float(r.get("team_size")))
        if 11 <= size <= 200:
            pts += WEIGHTS["size_fit"]
            reasons.append("team size fits")
        elif 5 <= size < 11:
            pts += WEIGHTS["size_fit"] / 2
    except (TypeError, ValueError):
        pass

    if _flag(r.get("recent_funding")):
        pts += WEIGHTS["recent_funding"]
        reasons.append("recent funding")
    if _flag(r.get("hiring_tech")):
        pts += WEIGHTS["hiring_tech"]
        reasons.append("hiring tech roles")

    # service fit (first matching rule wins) - edit to match what you actually sell
    if manual:
        seg = "Automation"
    elif no_app:
        seg = "Mobile App"
    elif _flag(r.get("recent_funding")) or _flag(r.get("hiring_tech")):
        seg = "MVP / Product Build"
    else:
        seg = "SaaS / Platform"

    return pd.Series({"score": round(pts), "segment": seg,
                      "signals": "; ".join(reasons)})


def score_df(df: pd.DataFrame) -> pd.DataFrame:
    scored = df.apply(score_lead, axis=1)
    out = pd.concat([df.reset_index(drop=True), scored.reset_index(drop=True)], axis=1)
    out["tier"] = pd.cut(out["score"], [-1, 39, 64, 100], labels=["C", "B", "A"])
    return out.sort_values("score", ascending=False).reset_index(drop=True)
