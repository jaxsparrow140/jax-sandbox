import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional, Tuple

import requests
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

STANFORD_API = "https://explorecourses.stanford.edu/search"
XML_VIEW = "xml-20200810"

# Simple in-memory cache to avoid hammering the registry.
_CACHE = {}
_CACHE_TTL_SECONDS = 60

QUARTERS = ["Autumn", "Winter", "Spring", "Summer"]


def _now() -> float:
    return time.time()


def _cache_get(key):
    hit = _CACHE.get(key)
    if not hit:
        return None
    ts, val = hit
    if _now() - ts > _CACHE_TTL_SECONDS:
        _CACHE.pop(key, None)
        return None
    return val


def _cache_set(key, val):
    _CACHE[key] = (_now(), val)


def _units_str(units_min: str, units_max: str) -> str:
    units_min = (units_min or "").strip()
    units_max = (units_max or "").strip()
    if units_min and units_max and units_min != units_max:
        return f"{units_min}-{units_max}"
    return units_min or units_max or "TBD"


def _text(el) -> str:
    if el is None:
        return ""
    return (el.text or "").strip()


def _split_days(days_text: str):
    # The API returns days as text with newlines/whitespace.
    s = re.sub(r"\s+", " ", (days_text or "").strip())
    if not s:
        return []
    parts = [p.strip() for p in s.split(" ") if p.strip()]
    # Day names are single tokens (Monday, Tuesday, ...)
    return parts


def _parse_course(course_el, quarter_filter: Optional[str] = None):
    subject = _text(course_el.find("subject"))
    code = _text(course_el.find("code"))
    course_code = " ".join([p for p in [subject, code] if p])

    title = _text(course_el.find("title"))
    description = _text(course_el.find("description"))

    units = _units_str(_text(course_el.find("unitsMin")), _text(course_el.find("unitsMax")))

    year = _text(course_el.find("year"))

    # Sections (these are what you actually schedule)
    sections_out = []
    terms = set()

    sections_el = course_el.find("sections")
    if sections_el is not None:
        for section_el in sections_el.findall("section"):
            term = _text(section_el.find("term"))
            if term:
                terms.add(term)

            if quarter_filter and (not term or not term.endswith(quarter_filter)):
                continue

            schedules_out = []
            schedules_el = section_el.find("schedules")
            if schedules_el is not None:
                for sched_el in schedules_el.findall("schedule"):
                    days = _split_days(_text(sched_el.find("days")))
                    start_time = _text(sched_el.find("startTime"))
                    end_time = _text(sched_el.find("endTime"))
                    start_date = _text(sched_el.find("startDate"))
                    end_date = _text(sched_el.find("endDate"))
                    location = _text(sched_el.find("location"))

                    # Skip truly empty schedule rows.
                    if not (days or start_time or end_time or location):
                        continue

                    instructors = []
                    instr_el = sched_el.find("instructors")
                    if instr_el is not None:
                        for i_el in instr_el.findall("instructor"):
                            name = _text(i_el.find("name"))
                            if name:
                                instructors.append(name)

                    schedules_out.append(
                        {
                            "days": days,
                            "startTime": start_time,
                            "endTime": end_time,
                            "startDate": start_date,
                            "endDate": end_date,
                            "location": location,
                            "instructors": instructors,
                        }
                    )

            sec_units = _text(section_el.find("units"))

            sections_out.append(
                {
                    "classId": _text(section_el.find("classId")),
                    "term": term,
                    "termId": _text(section_el.find("termId")),
                    "component": _text(section_el.find("component")),
                    "sectionNumber": _text(section_el.find("sectionNumber")),
                    "enrollStatus": _text(section_el.find("enrollStatus")),
                    "units": sec_units or units,
                    "schedules": schedules_out,
                }
            )

    return {
        "year": year,
        "code": course_code,
        "title": title,
        "units": units,
        "description": description,
        "terms": sorted(terms),
        "sections": sections_out,
    }


def stanford_search(query: str, academic_year: Optional[str] = None, quarter: Optional[str] = None, limit: int = 20):
    query = (query or "").strip()
    if not query:
        return []

    academic_year = (academic_year or "").strip() or None
    quarter = (quarter or "").strip() or None
    if quarter and quarter not in QUARTERS:
        quarter = None

    cache_key = ("search", query, academic_year, quarter, limit)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    params = {
        "q": query,
        "view": XML_VIEW,
        "filter-coursestatus-Active": "on",
    }
    # This API expects academicYear as an 8-digit string like 20252026
    if academic_year:
        params["academicYear"] = academic_year

    resp = requests.get(STANFORD_API, params=params, timeout=10)
    resp.raise_for_status()

    root = ET.fromstring(resp.text)

    courses = []
    # Only parse top-level <course> children under <courses>
    courses_el = root.find("courses")
    if courses_el is None:
        return []

    for course_el in courses_el.findall("course"):
        courses.append(_parse_course(course_el, quarter_filter=quarter))
        if len(courses) >= limit:
            break

    _cache_set(cache_key, courses)
    return courses


def _score_course_for_gsb_ai(course) -> Tuple[int, str, str]:
    """Return (score, category, why_gsb)."""
    """Return (score, category, why_gsb)"""

    text = (f"{course.get('code','')} {course.get('title','')} {course.get('description','')}"
            .lower())

    ai_score = 0
    if re.search(r"\b(machine learning|deep learning|artificial intelligence|reinforcement learning)\b", text):
        ai_score += 10
    if re.search(r"\b(foundation model|large language model|llm|generative ai|diffusion)\b", text):
        ai_score += 12
    if re.search(r"\b(nlp|natural language|vision|computer vision|graph neural|transformer)\b", text):
        ai_score += 6
    if re.search(r"\b(data science|causal|inference|prediction|forecast|statistics)\b", text):
        ai_score += 4
    if re.search(r"\b(ethics|fairness|accountability|privacy|policy|governance|regulation)\b", text):
        ai_score += 4

    biz_score = 0
    if re.search(r"\b(business|strategy|entrepreneur|venture|management|organization|marketing|finance|product|operations|decision)\b", text):
        biz_score += 5

    subj = (course.get("code", "").split(" ")[:1] or [""])[0]
    if subj in {"GSBGEN", "STRAMGT", "OB", "MKTG", "FINANCE", "MS&E", "ECON", "PUBLPOL", "POLISCI"}:
        biz_score += 4
    if subj in {"CS", "STATS", "EE", "CME"}:
        ai_score += 2

    score = ai_score + biz_score

    # Category (simple heuristic)
    if re.search(r"\b(foundation model|large language model|llm|generative ai)\b", text):
        category = "Generative AI / Foundation Models"
    elif re.search(r"\b(machine learning|deep learning|reinforcement learning)\b", text):
        category = "Core ML"
    elif re.search(r"\b(ethics|policy|governance|regulation|privacy|fairness)\b", text):
        category = "AI Ethics / Policy"
    elif re.search(r"\b(data science|statistics|causal|inference|decision)\b", text):
        category = "Data / Decision-Making"
    else:
        category = "AI-adjacent"

    # Why (template)
    if biz_score >= 7 and ai_score >= 10:
        why = "Strong AI content with direct strategy/decision-making relevance — ideal for a GSB lens."
    elif ai_score >= 12:
        why = "Deep technical AI course that builds real fluency (even if you're not coding full-time)."
    elif biz_score >= 7:
        why = "Business-facing framing; good if you want to lead AI teams and make better AI product/strategy calls."
    elif re.search(r"\b(ethics|policy|governance|regulation)\b", text):
        why = "A must if you're thinking about AI risk, regulation, and responsible deployment in industry."
    else:
        why = "Worth a look if you want AI context without committing to the most math-heavy track."

    return score, category, why


def recommend_gsb_ai(academic_year: Optional[str] = None, quarter: Optional[str] = None, limit: int = 12):
    seeds = [
        "machine learning",
        "artificial intelligence",
        "foundation models",
        "large language models",
        "generative ai",
        "ai policy",
        "ai ethics",
        "data science",
        "causal inference",
        "decision making",
    ]

    seen = {}
    for q in seeds:
        for c in stanford_search(q, academic_year=academic_year, quarter=quarter, limit=25):
            key = c.get("code")
            if key and key not in seen:
                seen[key] = c

    scored = []
    for c in seen.values():
        score, category, why = _score_course_for_gsb_ai(c)
        # Keep it AI-centric.
        if score < 12:
            continue

        # If a quarter filter is set, prefer courses with at least one section in that quarter.
        if quarter and not c.get("sections"):
            continue

        # Provide a convenient ExploreCourses link.
        ay = academic_year or ""
        query = requests.utils.quote(c.get("code", ""))
        link = f"https://explorecourses.stanford.edu/search?view=catalog&filter-coursestatus-Active=on&page=0&academicYear={ay}&q={query}" if ay else f"https://explorecourses.stanford.edu/search?view=catalog&filter-coursestatus-Active=on&page=0&q={query}"

        scored.append(
            {
                **c,
                "category": category,
                "why_gsb": why,
                "link": link,
                "score": score,
            }
        )

    scored.sort(key=lambda x: (-x["score"], x.get("code", "")))
    return scored[:limit]


def _default_next_quarter_and_year():
    # Rough Stanford quarter mapping.
    # - Autumn: Sep-Dec
    # - Winter: Jan-Mar
    # - Spring: Mar-Jun
    # - Summer: Jun-Aug
    now = datetime.now()
    m = now.month

    if m in (9, 10, 11, 12):
        next_q = "Winter"
    elif m in (1, 2):
        next_q = "Spring"
    elif m in (3, 4, 5):
        next_q = "Summer"
    else:
        next_q = "Autumn"

    # Academic year starts in Autumn.
    if m >= 9:
        start = now.year
    else:
        start = now.year - 1
    end = start + 1
    academic_year = f"{start}{end}"

    return next_q, academic_year


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/meta")
def meta():
    q, ay = _default_next_quarter_and_year()
    # Provide a small window of years for convenience
    start = int(ay[:4])
    years = [f"{y}{y+1}" for y in range(start - 2, start + 3)]
    return jsonify(
        {
            "defaultQuarter": q,
            "defaultAcademicYear": ay,
            "quarters": QUARTERS,
            "academicYears": years,
        }
    )


@app.route("/api/search")
def search():
    query = request.args.get("q", "").strip()
    academic_year = request.args.get("year", "").strip() or None
    quarter = request.args.get("quarter", "").strip() or None
    scheduled_only = request.args.get("scheduledOnly", "").strip().lower() in {"1", "true", "yes", "on"}

    if not query:
        return jsonify([])

    try:
        courses = stanford_search(query, academic_year=academic_year, quarter=quarter, limit=20)
        if quarter and scheduled_only:
            courses = [c for c in courses if c.get("sections")]
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch from Stanford registry: {str(e)}"}), 502
    except ET.ParseError:
        return jsonify({"error": "Failed to parse Stanford registry response"}), 502

    return jsonify(courses)


@app.route("/api/recommendations")
def recommendations():
    academic_year = request.args.get("year", "").strip() or None
    quarter = request.args.get("quarter", "").strip() or None

    try:
        recs = recommend_gsb_ai(academic_year=academic_year, quarter=quarter, limit=12)
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch from Stanford registry: {str(e)}"}), 502
    except ET.ParseError:
        return jsonify({"error": "Failed to parse Stanford registry response"}), 502

    # Remove internal score before sending to UI
    for r in recs:
        r.pop("score", None)
    return jsonify(recs)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
