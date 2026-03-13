"""
Stanford Course Scheduler - Flask backend.
"""

import json
import os
from flask import Flask, render_template, jsonify, request

from scraper import get_courses
from search import search_courses
from recommendations import get_recommendations

app = Flask(__name__)

# Load courses on startup
COURSES = []


def init_courses():
    global COURSES
    COURSES = get_courses()
    print(f"Loaded {len(COURSES)} courses")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/courses")
def api_courses():
    """Return all courses."""
    return jsonify(COURSES)


@app.route("/api/search")
def api_search():
    """Natural language search."""
    q = request.args.get("q", "").strip()
    dept = request.args.get("dept", "").strip()
    days = request.args.get("days", "").strip()
    units = request.args.get("units", "").strip()

    # Start with NL search or all courses
    if q:
        results = search_courses(q, COURSES, limit=50)
    else:
        results = list(COURSES)

    # Apply filters
    if dept:
        results = [c for c in results if c["department"].upper() == dept.upper()]

    if days:
        day_list = days.split(",")
        results = [c for c in results
                   if any(d in c.get("schedule", "") for d in day_list)]

    if units:
        try:
            target = int(units)
            filtered = []
            for c in results:
                u = c.get("units", "")
                if not u:
                    continue
                if "-" in u:
                    lo, hi = u.split("-")
                    if int(lo) <= target <= int(hi):
                        filtered.append(c)
                elif u.isdigit() and int(u) == target:
                    filtered.append(c)
            results = filtered
        except ValueError:
            pass

    return jsonify(results)


@app.route("/api/recommendations")
def api_recommendations():
    """Get curated AI course recommendations."""
    return jsonify(get_recommendations(COURSES))


@app.route("/api/check-conflicts", methods=["POST"])
def api_check_conflicts():
    """Check for time conflicts in a list of courses."""
    schedule = request.json or []
    conflicts = find_conflicts(schedule)
    return jsonify({"conflicts": conflicts})


def parse_time_range(schedule_str: str) -> list[tuple[str, int, int]]:
    """Parse schedule string into list of (day, start_minutes, end_minutes)."""
    import re
    if not schedule_str:
        return []

    slots = []
    # Extract days
    days = re.findall(r'(Mon|Tue|Wed|Thu|Fri|Sat|Sun)', schedule_str)
    # Try "1:30 PM - 2:50 PM" format first
    time_match = re.search(
        r'(\d{1,2}):(\d{2})\s*(AM|PM)\s*[-\u2013]\s*(\d{1,2}):(\d{2})\s*(AM|PM)',
        schedule_str, re.I
    )
    if not time_match:
        # Try "1:30-2:50 PM" format (single AM/PM at end)
        time_match2 = re.search(
            r'(\d{1,2}):(\d{2})\s*[-\u2013]\s*(\d{1,2}):(\d{2})\s*(AM|PM)',
            schedule_str, re.I
        )
        if time_match2 and days:
            sh = int(time_match2.group(1))
            sm = int(time_match2.group(2))
            eh = int(time_match2.group(3))
            em = int(time_match2.group(4))
            period = time_match2.group(5).upper()
            # Both times share the same period
            start_min = (sh % 12) * 60 + sm + (720 if period == "PM" else 0)
            end_min = (eh % 12) * 60 + em + (720 if period == "PM" else 0)
            for day in days:
                slots.append((day, start_min, end_min))
        return slots

    if not time_match or not days:
        return []

    sh, sm, sp = int(time_match.group(1)), int(time_match.group(2)), time_match.group(3).upper()
    eh, em, ep = int(time_match.group(4)), int(time_match.group(5)), time_match.group(6).upper()

    start_min = (sh % 12) * 60 + sm + (720 if sp == "PM" else 0)
    end_min = (eh % 12) * 60 + em + (720 if ep == "PM" else 0)

    for day in days:
        slots.append((day, start_min, end_min))

    return slots


def find_conflicts(schedule: list[dict]) -> list[dict]:
    """Find all time conflicts among scheduled courses."""
    conflicts = []
    parsed = [(c, parse_time_range(c.get("schedule", ""))) for c in schedule]

    for i in range(len(parsed)):
        for j in range(i + 1, len(parsed)):
            c1, slots1 = parsed[i]
            c2, slots2 = parsed[j]
            for day1, s1, e1 in slots1:
                for day2, s2, e2 in slots2:
                    if day1 == day2 and s1 < e2 and s2 < e1:
                        conflicts.append({
                            "course1": c1["code"],
                            "course2": c2["code"],
                            "day": day1,
                            "detail": f"{c1['code']} and {c2['code']} overlap on {day1}"
                        })
    return conflicts


if __name__ == "__main__":
    init_courses()
    app.run(debug=True, port=5050)
