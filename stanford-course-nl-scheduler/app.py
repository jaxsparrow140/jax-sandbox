from __future__ import annotations

import datetime as dt
import re
from pathlib import Path
from typing import Optional

import streamlit as st

from src import db as dbmod
from src.explorecourses import filter_courses_for_term, parse_term, search_courses
from src.models import Course, Section, Term
from src.nl import NLAction, parse as parse_nl
from src.recommend import ai_score, recommend_for_term


APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
CACHE_DIR = APP_DIR / ".cache"
DB_PATH = DATA_DIR / "plan.db"


def _guess_academic_year(today: dt.date) -> str:
    # Stanford academic year starts in Autumn.
    if today.month >= 9:
        return f"{today.year}-{today.year+1}"
    return f"{today.year-1}-{today.year}"


def _quarters() -> list[str]:
    return ["Autumn", "Winter", "Spring", "Summer"]


def _default_quarter(today: dt.date) -> str:
    # Rough mapping; user can override.
    if today.month in (9, 10, 11, 12):
        return "Autumn"
    if today.month in (1, 2, 3):
        return "Winter"
    if today.month in (4, 5, 6):
        return "Spring"
    return "Summer"


def _next_quarter(q: str) -> str:
    qs = _quarters()
    i = qs.index(q)
    return qs[(i + 1) % len(qs)]


def _pick_section_for_term(course: Course, term: Term) -> Optional[Section]:
    target = term.label
    secs = [s for s in course.sections if s.term == target]
    if not secs:
        return None
    # Prefer lecture.
    for s in secs:
        if s.component.upper() == "LEC":
            return s
    return secs[0]


def _render_course_card(course: Course, term: Term, conn) -> None:
    st.markdown(f"**{course.course_id}** — {course.title}")
    if course.description:
        st.caption(course.description)

    terms = course.offered_terms()
    if terms:
        st.write("Offered:", ", ".join(terms[:8]) + (" …" if len(terms) > 8 else ""))

    col1, col2 = st.columns([1, 2])
    with col1:
        add_label = f"Add {course.course_id}"
        if st.button(add_label, key=f"add::{term.label}::{course.year}::{course.subject}::{course.code}"):
            section = _pick_section_for_term(course, term)
            ok = dbmod.add_course(conn, term=term, course=course, section=section)
            if ok:
                st.success(f"Added to plan: {course.course_id} ({term.quarter})")
            else:
                st.info("Already in your plan (or could not add).")

    with col2:
        st.write(f"AI-ness score: `{ai_score(course):.1f}`")


def _render_plan(conn, term: Term) -> None:
    rows = dbmod.list_plan(conn, term=term)
    if not rows:
        st.info("No courses in your plan for this term yet.")
        return

    for r in rows:
        cid = f"{r['subject']} {r['code']}"
        st.markdown(f"**{cid}** — {r['title']}")
        meta = []
        if r.get("units"):
            meta.append(f"Units: {r['units']}")
        if r.get("component"):
            meta.append(f"Component: {r['component']}")
        if meta:
            st.caption(" · ".join(meta))

        cols = st.columns([1, 4])
        with cols[0]:
            if st.button(f"Remove {cid}", key=f"rm::{term.label}::{cid}"):
                ok = dbmod.remove_course(conn, term=term, subject=r["subject"], code=r["code"])
                if ok:
                    st.success(f"Removed {cid}")
                    st.rerun()
        with cols[1]:
            if r.get("source_url"):
                st.link_button("Open in ExploreCourses", r["source_url"], use_container_width=False)


@st.cache_data(show_spinner=False)
def _cached_search(query: str, term_label: str) -> list[Course]:
    term = parse_term(term_label)
    courses = search_courses(query, cache_dir=CACHE_DIR)
    if term:
        courses = filter_courses_for_term(courses, term)
    # Rank locally.
    qn = re.sub(r"\s+", " ", query.strip().lower())

    def score(c: Course) -> float:
        s = 0.0
        if qn.replace(" ", "") == (c.subject + c.code).lower():
            s += 100
        if qn in (c.subject + " " + c.code).lower():
            s += 20
        text = (c.title + " " + c.description).lower()
        for tok in qn.split():
            if tok in text:
                s += 2
        s += ai_score(c)
        return s

    courses.sort(key=score, reverse=True)
    return courses


@st.cache_data(show_spinner=False)
def _cached_recommend(term_label: str) -> list[Course]:
    term = parse_term(term_label)
    if not term:
        return []
    return recommend_for_term(term, cache_dir=CACHE_DIR)


def main() -> None:
    st.set_page_config(page_title="Stanford Course NL Scheduler", layout="wide")

    today = dt.date.today()
    ay_default = _guess_academic_year(today)
    q_default = _next_quarter(_default_quarter(today))

    st.title("Stanford Course Finder + Planner (NL)")

    with st.sidebar:
        st.header("Term")
        ay = st.text_input("Academic year", value=ay_default, help="e.g. 2025-2026")
        quarter = st.selectbox("Quarter", _quarters(), index=_quarters().index(q_default))
        term = Term(academic_year=ay.strip(), quarter=quarter)
        st.caption(f"Using term: **{term.label}**")

        st.divider()
        st.subheader("Your plan")

    conn = dbmod.connect(DB_PATH)

    with st.sidebar:
        _render_plan(conn, term)

    st.divider()

    # Chat-style NL box
    st.subheader("Natural language")
    st.caption("Try: `recommend ai courses`, `find generative ai`, `add CS 229`, `show my plan`")

    if "chat" not in st.session_state:
        st.session_state.chat = []

    for role, text in st.session_state.chat:
        with st.chat_message(role):
            st.write(text)

    msg = st.chat_input("What do you want to do?")
    if msg:
        st.session_state.chat.append(("user", msg))
        act: NLAction = parse_nl(msg)

        with st.chat_message("assistant"):
            if act.type == "help":
                st.write(
                    "Commands: recommend ai courses · search/find <query> · add <SUBJECT CODE> · remove <SUBJECT CODE> · show my plan"
                )

            elif act.type == "show_plan":
                st.write(f"Your plan for {term.label}:")
                _render_plan(conn, term)

            elif act.type == "recommend":
                st.write(f"AI-centric recommendations for **{term.label}** (ranked heuristically):")
                recs = _cached_recommend(term.label)
                if not recs:
                    st.info("No recommendations found for that term. Try changing academic year/quarter.")
                else:
                    for c in recs:
                        with st.expander(f"{c.course_id} — {c.title}", expanded=False):
                            _render_course_card(c, term, conn)

            elif act.type == "add" and act.subject and act.code:
                q = f"{act.subject}{act.code}"
                st.write(f"Searching for **{act.subject} {act.code}** in {term.label} …")
                courses = _cached_search(q, term.label)
                exact = [c for c in courses if c.subject == act.subject and c.code == act.code]
                picks = exact or courses
                if not picks:
                    st.warning("No matches found.")
                else:
                    # Show best few matches.
                    for c in picks[:5]:
                        with st.expander(f"{c.course_id} — {c.title}", expanded=True):
                            _render_course_card(c, term, conn)

            elif act.type == "remove" and act.subject and act.code:
                ok = dbmod.remove_course(conn, term=term, subject=act.subject, code=act.code)
                if ok:
                    st.success(f"Removed {act.subject} {act.code} from {term.label}.")
                else:
                    st.info("Not in plan (or nothing removed).")

            else:
                query = act.query or msg
                st.write(f"Search results for: **{query}** (filtered to {term.label})")
                courses = _cached_search(query, term.label)
                if not courses:
                    st.warning("No results.")
                else:
                    for c in courses[:30]:
                        with st.expander(f"{c.course_id} — {c.title}", expanded=False):
                            _render_course_card(c, term, conn)
                    if len(courses) > 30:
                        st.caption(f"Showing top 30 of {len(courses)} results.")

        # Note: Streamlit will rerun automatically on most interactions (buttons/chat input).
        # We avoid forcing a rerun here so search results stay visible after processing.


if __name__ == "__main__":
    main()
