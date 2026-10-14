"""Create SYNTHETIC leads so you can test the pipeline. NOT real companies - replace with real research."""
import random

import pandas as pd

INDUSTRIES = ["d2c", "clinic", "coaching", "retail", "logistics", "restaurant", "fitness", "manufacturing", "agency"]
CITIES = ["Jabalpur", "Indore", "Bhopal", "Nagpur", "Pune", "Jaipur", "Lucknow", "Bengaluru"]
FIRST = ["Aarav", "Meera", "Rohan", "Kavya", "Imran", "Neha", "Vikram", "Sana", "Arjun", "Pooja"]


def make(n=60, seed=7) -> pd.DataFrame:
    rnd = random.Random(seed)
    rows = []
    for i in range(1, n + 1):
        has_site = rnd.random() > 0.2
        rows.append({
            "company": f"Sample Business {i:02d}",
            "industry": rnd.choice(INDUSTRIES),
            "city": rnd.choice(CITIES),
            "website": f"sample-business-{i:02d}.example" if has_site else "",
            "contact_name": f"{rnd.choice(FIRST)} Sharma",
            "contact_role": rnd.choice(["Founder", "Co-founder", "Director", "Operations Head"]),
            "email": f"contact{i:02d}@sample-business-{i:02d}.example",
            "linkedin": f"https://linkedin.com/in/sample-{i:02d}",
            "team_size": rnd.choice([3, 8, 15, 25, 60, 120, 300]),
            "recent_funding": int(rnd.random() < 0.15),
            "hiring_tech": int(rnd.random() < 0.25),
            "has_mobile_app": int(rnd.random() < 0.3),
            "manual_workflow": int(rnd.random() < 0.4),
            "source": "SYNTHETIC - replace with real source",
        })
    return pd.DataFrame(rows)
