# Stanford Course NL Scheduler (simple)

A small Streamlit app for searching Stanford's course registry (ExploreCourses) and building a lightweight "plan" for an upcoming quarter.

## What it does

- Search Stanford ExploreCourses via the public `view=xml` endpoint
- Filter results to a selected academic year + quarter (Autumn/Winter/Spring/Summer)
- Add/remove courses to a local plan (SQLite)
- Natural-language command box ("find X", "add CS 229", "recommend AI courses", etc.)
- AI-centric recommendations tuned for a GSB-ish workflow (filters + scoring)

## Setup

```bash
cd stanford-course-nl-scheduler
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app stores your plan locally at `data/plan.db`.

## Natural-language examples

- `recommend ai courses`
- `find generative ai`
- `add CS 229`
- `add CS 224N`
- `remove CS 229`
- `show my plan`

## Notes / limitations

ExploreCourses' public XML search results do **not** include meeting times (days/hours/locations) in the serialized schedule objects, so this app focuses on **course discovery + quarter planning**, not a weekly calendar grid.
