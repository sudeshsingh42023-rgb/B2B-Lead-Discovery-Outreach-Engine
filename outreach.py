"""Generate a personalised 3-touch outreach sequence per lead."""
from datetime import date, timedelta

import pandas as pd

from .config import FOLLOWUP_DAYS, SENDER

# EDIT these templates - make them sound like you. Keep emails under ~90 words.
HOOKS = {
    "Automation": "I noticed {company} still handles {workflow} manually, which usually means hours lost every week and missed orders.",
    "Mobile App": "I noticed {company} doesn't have a mobile app yet, while most of your customers are on their phones all day.",
    "MVP / Product Build": "I saw {company} is investing in its tech team, so I wanted to share how we help teams ship product faster.",
    "SaaS / Platform": "I came across {company} and noticed a few gaps on your website that may be costing you enquiries.",
}
VALUE = {
    "Automation": "automate bookings, order intake and follow-ups so your team stops chasing things on WhatsApp",
    "Mobile App": "build a simple customer app (ordering, bookings, loyalty) in weeks, not months",
    "MVP / Product Build": "take an idea or an internal tool to a working MVP quickly, with a team that owns delivery",
    "SaaS / Platform": "modernise your web presence and build the tools your customers keep asking for",
}
SHORT = {
    "Automation": "automate bookings and order handling",
    "Mobile App": "launch a customer app",
    "MVP / Product Build": "ship a new product or MVP",
    "SaaS / Platform": "upgrade your web platform",
}

T1 = """Hi {first_name},

{hook}

At {sender_company} we {value}.

Would a 15-minute call this week be worth it? I can share 2-3 specific ideas for {company} beforehand.

Best,
{sender_name}
{sender_title}, {sender_company}"""

T2 = """Hi {first_name},

Quick follow-up on my note. Teams like {company} usually see the biggest win from one small fix first, and I have a suggestion for yours.

Happy to send it over in 3 lines, no call needed. Interested?

{sender_name}"""

T3 = """Hi {first_name},

I'll assume the timing isn't right and won't keep emailing. If {company} ever plans to {value_short}, I'd be glad to help.

Wishing you a great quarter,
{sender_name}"""

LINKEDIN_NOTE = ("Hi {first_name}, I work on growth at {sender_company}. "
                 "I had a couple of ideas for {company} around {topic}. Happy to connect!")
TOPIC = {"Automation": "automating bookings and orders", "Mobile App": "a customer app",
         "MVP / Product Build": "shipping product faster", "SaaS / Platform": "your web presence"}


def first_name(name) -> str:
    return str(name).split()[0] if isinstance(name, str) and name.strip() else "there"


def build_sequence(lead, start: date) -> list:
    seg = lead["segment"]
    ctx = {
        "first_name": first_name(lead.get("contact_name")),
        "company": lead["company"],
        "workflow": "bookings and orders",
        "sender_name": SENDER["name"], "sender_title": SENDER["title"],
        "sender_company": SENDER["company"],
        "value": VALUE[seg], "value_short": SHORT[seg],
        "topic": TOPIC[seg],
    }
    ctx["hook"] = HOOKS[seg].format(**ctx)
    touches = [
        ("Email", f"Idea for {lead['company']}", T1.format(**ctx)),
        ("Email", f"Re: Idea for {lead['company']}", T2.format(**ctx)),
        ("Email", f"Closing the loop, {lead['company']}", T3.format(**ctx)),
    ]
    rows = [{"company": lead["company"], "segment": seg, "touch": i + 1, "channel": ch,
             "send_date": (start + timedelta(days=FOLLOWUP_DAYS[i])).isoformat(),
             "to": lead.get("email", ""), "subject": sub, "body": body}
            for i, (ch, sub, body) in enumerate(touches)]
    rows.append({"company": lead["company"], "segment": seg, "touch": 1, "channel": "LinkedIn",
                 "send_date": start.isoformat(), "to": lead.get("linkedin", ""),
                 "subject": "", "body": LINKEDIN_NOTE.format(**ctx)[:295]})
    return rows


def build_all(scored: pd.DataFrame, start: date, min_score: int = 40, top=None) -> pd.DataFrame:
    sel = scored[scored["score"] >= min_score]
    if top:
        sel = sel.head(top)
    rows = []
    for _, lead in sel.iterrows():
        rows += build_sequence(lead, start)
    return pd.DataFrame(rows)
