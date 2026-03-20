# Stanford Course Scheduler (simple)

A lightweight web app for planning next quarter at Stanford.

- Uses Stanford’s **ExploreCourses XML** registry endpoint (no keys required)
- **Natural-language command box** (search / add / remove / recommend)
- Add **specific sections** (LEC/DIS/etc.) with meeting times when available
- Export your plan to an **.ics calendar**
- “AI-centric” recommendations tuned for a **GSB** lens (generated from the live registry; no hallucinated hardcoded list)

## Quickstart

```bash
cd stanford_scheduler
python3 -m pip install -r requirements.txt
python3 app.py
```

Open: http://localhost:5000

## Natural language examples

- `recommend ai courses for next quarter`
- `find foundation models`
- `find ai policy`
- `add CS 229`
- `add CS 229 section 01`
- `remove CS 229`
- `export ics`

## Notes / limitations

- ExploreCourses is a great registry, but **Axess is the source of truth** for enrollment.
- Some sections have missing/TBA meeting times; the app will skip those when exporting to .ics.
- The quarter/year picker filters to sections scheduled for that term when possible.
