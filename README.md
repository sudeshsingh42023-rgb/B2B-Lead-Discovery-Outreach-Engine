# B2B Lead Discovery & Outreach Engine

A Python tool that finds, scores and contacts small and mid-size businesses that are likely to need custom software,
then measures which messages actually get replies. Built for an outbound software-sales workflow
(Business Growth Intern, Isocode).

> **Status of the data:** `python main.py demo` creates **synthetic** companies only so you can test the pipeline.
> Replace them with real prospects (see "Using real data") before quoting any result.

## The problem
Outbound sales for a software studio is mostly manual: searching for prospects, guessing who needs what, writing
the same email 50 times, and forgetting follow-ups. This project turns that into a repeatable system:

```
leads.csv ──► enrich (visit sites) ──► score (0-100) ──► segment (service fit)
                                                         │
          report (reply rate by segment/touch) ◄── log ◄── outreach (3-touch sequence + LinkedIn note)
```

## What it does
| Step | Command | Output |
|---|---|---|
| 1. Add leads | fill `data/leads.csv` (template in `data/leads_template.csv`) | prospect list |
| 2. Enrich | `python main.py enrich` | adds site speed, HTTPS, mobile-friendly, booking, WhatsApp-only, app-link, copyright year |
| 3. Score | `python main.py score` | 0-100 score, tier A/B/C, service-fit segment, plain-English reasons |
| 4. Outreach | `python main.py outreach --start 2026-10-20 --min-score 40` | `outreach/sequence.csv`: 3 emails (day 0/3/7) + LinkedIn note per lead |
| 5. Log | `python main.py log --company "X" --touch 1 --sent 2026-10-20 --replied 1 --call 0` | `data/outreach_log.csv` |
| 6. Report | `python main.py report` | `reports/summary.md`: reply and call rates by segment, tier, touch, channel |

## Scoring model (edit in `src/config.py`)
| Signal | Points | Why it matters |
|---|---|---|
| Website gap (none, slow, no HTTPS, not mobile-friendly, outdated) | 20 | visible need for a rebuild |
| No mobile app (consumer-facing industries) | 15 | app opportunity |
| Manual workflow (WhatsApp/phone-only orders or bookings) | 25 | strongest automation signal |
| Team size 11-200 | 10 | can afford custom software |
| Recent funding | 15 | budget exists |
| Hiring tech roles | 15 | already investing in tech |

Segments (first rule that matches): **Automation** → **Mobile App** → **MVP / Product Build** → **SaaS / Platform**.

## Quick start
```bash
pip install -r requirements.txt
python main.py demo          # synthetic data, to test
python main.py score
python main.py outreach --start 2026-10-20 --top 10
python main.py report
```

## Using real data (do this before putting numbers on your resume)
1. Research 100-300 real prospects from public sources (Google Maps, LinkedIn company pages, startup directories,
   job boards) and fill `data/leads.csv`. Set `source` for every row.
2. Run `enrich` in small batches (it makes one request per site, with a delay). Respect each site's terms.
3. Review the top-scored leads by hand and sanity-check the signals.
4. Edit the templates in `src/outreach.py` so they sound like you; send 30-50 messages yourself.
5. Log every send and reply with `python main.py log ...`, then run `report`.
6. Check the segment and touch tables: they show which pitch and which follow-up actually work.

## Resume bullets (replace the brackets with your real numbers)
- Built a Python lead-generation engine that sourced and scored **[N]** SMB prospects on 6 digital-gap signals,
  cutting manual research time by **[X]%**.
- Designed segment-specific outreach with a 3-touch follow-up cadence; sent to **[N]** prospects and achieved a
  **[X]%** reply rate and **[N]** booked calls.
- Segmented leads into 4 service-fit categories; the best segment replied at **[X]%** vs **[Y]%** baseline.

## Project structure
```
main.py            CLI
src/config.py      sender details, weights, segments, follow-up days
src/enrich.py      website signal extraction
src/score.py       scoring + segment logic
src/outreach.py    email / LinkedIn templates and sequencing
src/tracker.py     outreach log + reporting
src/demo_data.py   synthetic data generator
data/              leads, scored leads, outreach log
outreach/          generated message sequences
reports/           summary.md
```

## Limitations and ideas
- Signals come from one page fetch per site; JS-heavy sites may be under-detected.
- Weights are judgement-based. Once you have 50+ outcomes, fit a logistic regression on reply/no-reply to learn them.
- Add: email finder/verification, A/B subject lines, LinkedIn export import, a Streamlit front end, or a handoff
  to the companion **Sales Pipeline CRM** project (import `data/leads_scored.csv`).
- Follow local rules on cold outreach and data privacy (include an opt-out line when emailing at scale).
