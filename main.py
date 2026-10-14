"""CLI for the B2B Lead Discovery & Outreach Engine.

    python main.py demo                       # create synthetic leads (to test)
    python main.py enrich                     # visit websites, extract signals
    python main.py score                      # score + segment leads
    python main.py outreach --start 2026-10-20 --min-score 40
    python main.py log --company "X" --touch 1 --channel Email --sent 2026-10-20 --replied 1 --call 0
    python main.py report
"""
import argparse
from datetime import date
from pathlib import Path

import pandas as pd

from src import demo_data, enrich as enr, outreach, score, tracker

D = Path("data")
LEADS, ENRICHED, SCORED = D / "leads.csv", D / "leads_enriched.csv", D / "leads_scored.csv"
LOG = D / "outreach_log.csv"


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("demo")
    e = sub.add_parser("enrich"); e.add_argument("--delay", type=float, default=1.0)
    sub.add_parser("score")
    o = sub.add_parser("outreach")
    o.add_argument("--start", default=date.today().isoformat())
    o.add_argument("--min-score", type=int, default=40)
    o.add_argument("--top", type=int)
    lg = sub.add_parser("log")
    lg.add_argument("--company", required=True); lg.add_argument("--touch", type=int, required=True)
    lg.add_argument("--channel", default="Email"); lg.add_argument("--sent", required=True)
    lg.add_argument("--replied", type=int, default=0); lg.add_argument("--reply-date", default="")
    lg.add_argument("--call", type=int, default=0); lg.add_argument("--notes", default="")
    sub.add_parser("report")
    a = ap.parse_args()

    D.mkdir(exist_ok=True)
    if a.cmd == "demo":
        demo_data.make().to_csv(LEADS, index=False)
        print(f"Wrote synthetic leads -> {LEADS}")
    elif a.cmd == "enrich":
        df = enr.enrich(pd.read_csv(LEADS), delay=a.delay)
        df.to_csv(ENRICHED, index=False)
        print(f"Enriched {len(df)} leads -> {ENRICHED}")
    elif a.cmd == "score":
        src = ENRICHED if ENRICHED.exists() else LEADS
        df = score.score_df(pd.read_csv(src))
        df.to_csv(SCORED, index=False)
        print(f"Scored {len(df)} leads from {src.name} -> {SCORED}")
        print(df["tier"].value_counts().to_string())
        print(df.groupby("segment")["score"].agg(["count", "mean"]).round(1).to_string())
    elif a.cmd == "outreach":
        seq = outreach.build_all(pd.read_csv(SCORED), date.fromisoformat(a.start), a.min_score, a.top)
        Path("outreach").mkdir(exist_ok=True)
        seq.to_csv("outreach/sequence.csv", index=False)
        print(f"Generated {len(seq)} messages for {seq['company'].nunique()} leads -> outreach/sequence.csv")
    elif a.cmd == "log":
        tracker.append_log(LOG, a.company, a.touch, a.channel, a.sent, a.replied, a.reply_date, a.call, a.notes)
        print("Logged.")
    elif a.cmd == "report":
        log = pd.read_csv(LOG) if LOG.exists() else pd.DataFrame(columns=tracker.LOG_COLS)
        md = tracker.report(pd.read_csv(SCORED), log)
        Path("reports").mkdir(exist_ok=True)
        Path("reports/summary.md").write_text(md)
        print(md)


if __name__ == "__main__":
    main()
