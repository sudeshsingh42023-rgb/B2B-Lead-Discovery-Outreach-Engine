"""Log outreach results and report reply/call rates by segment, tier and touch."""
import os

import pandas as pd

LOG_COLS = ["company", "touch", "channel", "sent_date", "replied", "reply_date", "call_booked", "notes"]


def append_log(path, company, touch, channel, sent_date, replied=0, reply_date="", call_booked=0, notes=""):
    row = pd.DataFrame([[company, touch, channel, sent_date, replied, reply_date, call_booked, notes]], columns=LOG_COLS)
    row.to_csv(path, mode="a", header=not os.path.exists(path), index=False)


def _table(df, by):
    g = df.groupby(by, observed=True).agg(prospects=("company", "nunique"), replies=("replied", "sum"),
                                          calls=("call_booked", "sum")).reset_index()
    g["reply_rate"] = (g["replies"] / g["prospects"]).map("{:.0%}".format)
    header = "| " + " | ".join(map(str, g.columns)) + " |"
    sep = "|" + "---|" * len(g.columns)
    body = ["| " + " | ".join(map(str, row)) + " |" for row in g.values.tolist()]
    return "\n".join([header, sep] + body)


def report(scored: pd.DataFrame, log: pd.DataFrame) -> str:
    lines = ["# Outreach report", ""]
    if log.empty:
        return "\n".join(lines + ["No outreach logged yet."])
    df = log.merge(scored[["company", "segment", "tier", "score"]], on="company", how="left")
    n = df["company"].nunique()
    replied = df.groupby("company")["replied"].max().sum()
    calls = df.groupby("company")["call_booked"].max().sum()
    lines += [f"- Prospects contacted: **{n}**",
              f"- Replies: **{int(replied)}** ({replied / n:.0%})",
              f"- Calls booked: **{int(calls)}** ({calls / n:.0%})", ""]
    for title, by in [("By segment", "segment"), ("By lead tier", "tier"),
                      ("By touch number", "touch"), ("By channel", "channel")]:
        lines += [f"## {title}", "", _table(df, by), ""]
    return "\n".join(lines)
