"""Central config: edit weights, sender details and segments here."""

SENDER = {
    "name": "Sudesh Singh",
    "title": "Business Growth Intern",
    "company": "Isocode",          # EDIT: how you introduce the company
}

# Scoring weights (must sum to 100). Tune these after you see real reply data.
WEIGHTS = {
    "website_gap": 20,      # no site / slow / not mobile friendly / outdated
    "no_app": 15,           # consumer-facing business with no mobile app
    "manual_workflow": 25,  # orders/bookings via WhatsApp or phone only
    "size_fit": 10,         # team size 11-200 = can afford custom software
    "recent_funding": 15,   # budget exists
    "hiring_tech": 15,      # they are already investing in tech
}

CONSUMER_INDUSTRIES = {
    "d2c", "retail", "clinic", "healthcare", "education", "coaching",
    "restaurant", "salon", "fitness", "travel", "logistics",
}

SEGMENTS = ["Automation", "Mobile App", "MVP / Product Build", "SaaS / Platform"]

FOLLOWUP_DAYS = [0, 3, 7]   # touch 1, 2, 3 (days after campaign start)
