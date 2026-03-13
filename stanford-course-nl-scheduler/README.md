# Stanford Course NL Scheduler

A Streamlit app for finding Stanford courses using natural language and the ExploreCourses public XML API. Targeted at GSB students interested in AI/ML.

![Screenshot placeholder](docs/screenshot.png)

## Features

- **Natural language interface** — type what you want and the app figures it out
- **Curated GSB AI recommendations** — hand-picked Tier 1 (Core AI) and Tier 2 (Strategy & Policy) courses
- **Course info lookup** — "tell me about CS 229" shows a detailed card without adding to plan
- **Smart add/remove** — "put CS 224N in my schedule", "drop CS 229 from my plan"
- **Stanford-themed UI** — cardinal red accents, emoji badges by department, tier grouping
- **SQLite plan persistence** — your plan survives across sessions
- **No API keys needed** — uses the free ExploreCourses XML endpoint

## Quick Start

```bash
cd stanford-course-nl-scheduler
./run.sh
```

Or manually:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app stores your plan locally at `data/plan.db`.

## Natural Language Examples

| What you type | What happens |
|---|---|
| `recommend ai courses` | Curated GSB AI picks, grouped by tier |
| `what courses are there about prompt engineering` | Keyword search |
| `I want to learn about transformers` | Keyword search |
| `show me CS and MS&E courses on AI ethics` | Keyword search |
| `tell me about CS 229` | Detailed course info card |
| `how many units is CS 224N` | Course info with units |
| `add CS 229` | Search and add to plan |
| `put STATS 315A in my schedule` | Add to plan |
| `drop CS 229 from my plan` | Remove from plan |
| `I do not want CS 229 anymore` | Remove from plan |
| `show my plan` | View current plan |

## Architecture

- `app.py` — Streamlit UI with Stanford-themed CSS
- `src/nl.py` — Rule-based NL parser (regex, no LLM calls)
- `src/recommend.py` — Curated course list + heuristic scoring
- `src/explorecourses.py` — ExploreCourses XML API client with caching
- `src/db.py` — SQLite plan storage
- `src/models.py` — Data models (Course, Section, Term)

## Notes / Limitations

- ExploreCourses' public XML search does **not** include meeting times, so this app focuses on course discovery + quarter planning, not a weekly calendar grid.
- All NL parsing is rule-based — no paid LLM API calls.
- Only requires `streamlit` and `requests` as Python dependencies.
