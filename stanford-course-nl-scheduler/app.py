from __future__ import annotations

import datetime as dt
import re
from pathlib import Path
from typing import Optional

import streamlit as st

from src import db as dbmod
from src.explorecourses import course_url, filter_courses_for_term, parse_term, search_courses
from src.models import Course, Section, Term
from src.nl import NLAction, parse as parse_nl
from src.recommend import ai_score, get_blurb, get_tier, recommend_for_term


APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
CACHE_DIR = APP_DIR / ".cache"
DB_PATH = DATA_DIR / "plan.db"


# ---------------------------------------------------------------------------
# Stanford-themed CSS
# ---------------------------------------------------------------------------

STANFORD_CSS = """
<style>
    /* Stanford cardinal red accents */
    .stApp {
        font-family: 'Source Sans Pro', sans-serif;
    }
    .stApp > header {
        background-color: #8C1515;
    }
    div[data-testid="stSidebar"] {
        background-color: #f7f3f0;
        border-right: 3px solid #8C1515;
    }
    div[data-testid="stSidebar"] h1,
    div[data-testid="stSidebar"] h2,
    div[data-testid="stSidebar"] h3 {
        color: #8C1515;
    }
    .tier-badge-1 {
        background-color: #8C1515;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
        font-weight: 600;
    }
    .tier-badge-2 {
        background-color: #2e2d29;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
        font-weight: 600;
    }
    .subject-badge {
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 0.85em;
        font-weight: 600;
    }
    .unit-pill {
        background-color: #e8e3df;
        color: #2e2d29;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: 600;
    }
    .welcome-box {
        background: linear-gradient(135deg, #8C1515 0%, #b83a3a 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    .welcome-box h2 { color: white !important; margin-top: 0; }
    .welcome-box p { color: #f0e0e0; }
    .course-info-card {
        background: #fafafa;
        border-left: 4px solid #8C1515;
        padding: 1rem 1.5rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
    }
    .blurb-text {
        color: #555;
        font-style: italic;
        font-size: 0.9em;
        margin-top: 4px;
    }
</style>
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SUBJECT_EMOJI = {
    "CS": "\U0001F916",        # 🤖
    "EE": "\U0001F916",
    "STATS": "\U0001F4CA",     # 📊
    "CME": "\U0001F4CA",
    "MS&E": "\U0001F4BC",     # 💼
    "MGTECON": "\U0001F4BC",
    "OIT": "\U0001F4BC",
    "GSBGEN": "\U0001F4BC",
    "LAW": "\u2696\uFE0F",    # ⚖️
    "PUBLPOL": "\u2696\uFE0F",
    "COMM": "\U0001F4E1",     # 📡
    "LINGUIST": "\U0001F4AC", # 💬
    "SYMSYS": "\U0001F9E0",   # 🧠
}


def _subject_emoji(subject: str) -> str:
    return SUBJECT_EMOJI.get(subject, "\U0001F4D6")  # 📖 default


def _guess_academic_year(today: dt.date) -> str:
    if today.month >= 9:
        return f"{today.year}-{today.year+1}"
    return f"{today.year-1}-{today.year}"


def _quarters() -> list[str]:
    return ["Autumn", "Winter", "Spring", "Summer"]


def _default_quarter(today: dt.date) -> str:
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
    for s in secs:
        if s.component.upper() == "LEC":
            return s
    return secs[0]


def _get_units(course: Course) -> str:
    """Get units string from any section."""
    for s in course.sections:
        if s.units:
            return s.units
    return ""


def _get_instructors(course: Course) -> str:
    """Get instructors from lecture section if available."""
    for s in course.sections:
        if s.component.upper() == "LEC" and s.instructors:
            return s.instructors
    for s in course.sections:
        if s.instructors:
            return s.instructors
    return ""


def _render_course_card(course: Course, term: Term, conn, *, show_blurb: bool = False) -> None:
    emoji = _subject_emoji(course.subject)
    units = _get_units(course)
    instructors = _get_instructors(course)

    # Header with emoji badge
    header = f"{emoji} **{course.course_id}** — {course.title}"
    if units:
        header += f"  `{units} units`"
    st.markdown(header)

    if instructors:
        st.caption(f"Instructor(s): {instructors}")

    if show_blurb:
        blurb = get_blurb(course)
        if blurb:
            st.markdown(f'<p class="blurb-text">{blurb}</p>', unsafe_allow_html=True)

    if course.description:
        st.caption(course.description[:300] + ("..." if len(course.description) > 300 else ""))

    terms = course.offered_terms()
    if terms:
        st.write("Offered:", ", ".join(terms[:6]) + (" ..." if len(terms) > 6 else ""))

    col1, col2 = st.columns([1, 1])
    with col1:
        add_label = f"\u2795 Add {course.course_id} to Plan"
        if st.button(add_label, key=f"add::{term.label}::{course.year}::{course.subject}::{course.code}",
                     type="primary"):
            section = _pick_section_for_term(course, term)
            ok = dbmod.add_course(conn, term=term, course=course, section=section)
            if ok:
                st.success(f"Added to plan: {course.course_id} ({term.quarter})")
            else:
                st.info("Already in your plan.")
    with col2:
        tier = get_tier(course)
        if tier == 1:
            st.markdown('<span class="tier-badge-1">Tier 1: Core AI</span>', unsafe_allow_html=True)
        elif tier == 2:
            st.markdown('<span class="tier-badge-2">Tier 2: Strategy</span>', unsafe_allow_html=True)


def _render_course_info(course: Course, term: Term, conn) -> None:
    """Render a detailed info card for a single course."""
    emoji = _subject_emoji(course.subject)
    units = _get_units(course)
    instructors = _get_instructors(course)

    st.markdown(f"### {emoji} {course.course_id} — {course.title}")

    blurb = get_blurb(course)
    if blurb:
        st.markdown(f'<p class="blurb-text">{blurb}</p>', unsafe_allow_html=True)

    info_parts = []
    if units:
        info_parts.append(f"**Units:** {units}")
    if instructors:
        info_parts.append(f"**Instructor(s):** {instructors}")

    tier = get_tier(course)
    if tier:
        tier_label = "Tier 1: Core AI" if tier == 1 else "Tier 2: Strategy & Policy"
        info_parts.append(f"**GSB AI Tier:** {tier_label}")

    terms = course.offered_terms()
    if terms:
        info_parts.append(f"**Offered:** {', '.join(terms[:8])}")

    url = course_url(course.subject, course.code, academic_year=term.academic_year)
    info_parts.append(f"**[View on ExploreCourses]({url})**")

    st.markdown(" | ".join(info_parts))

    if course.description:
        st.markdown(course.description)

    st.markdown("---")
    add_label = f"\u2795 Add {course.course_id} to Plan"
    if st.button(add_label, key=f"info_add::{course.subject}::{course.code}", type="primary"):
        section = _pick_section_for_term(course, term)
        ok = dbmod.add_course(conn, term=term, course=course, section=section)
        if ok:
            st.success(f"Added to plan: {course.course_id} ({term.quarter})")
        else:
            st.info("Already in your plan.")


def _render_plan(conn, term: Term) -> None:
    rows = dbmod.list_plan(conn, term=term)
    if not rows:
        st.info("No courses in your plan for this term yet.")
        return

    # Total units
    total_units = 0
    for r in rows:
        try:
            u = r.get("units", "")
            if u:
                # Handle ranges like "3-5" — take the first number
                num = int(re.match(r"(\d+)", str(u)).group(1))
                total_units += num
        except Exception:
            pass

    st.markdown(f"**Total units: {total_units}**")
    st.markdown("---")

    for r in rows:
        cid = f"{r['subject']} {r['code']}"
        emoji = _subject_emoji(r['subject'])
        meta_parts = []
        if r.get("units"):
            meta_parts.append(f"{r['units']} units")
        if r.get("instructors"):
            meta_parts.append(r['instructors'][:40])
        meta = " · ".join(meta_parts)
        st.markdown(f"{emoji} **{cid}** — {r['title']}")
        if meta:
            st.caption(meta)

        cols = st.columns([1, 1])
        with cols[0]:
            if st.button(f"Remove", key=f"rm::{term.label}::{cid}"):
                ok = dbmod.remove_course(conn, term=term, subject=r["subject"], code=r["code"])
                if ok:
                    st.rerun()
        with cols[1]:
            if r.get("source_url"):
                st.link_button("ExploreCourses", r["source_url"], use_container_width=False)


def _clear_plan(conn, term: Term) -> None:
    """Remove all courses from plan for this term."""
    rows = dbmod.list_plan(conn, term=term)
    for r in rows:
        dbmod.remove_course(conn, term=term, subject=r["subject"], code=r["code"])


# ---------------------------------------------------------------------------
# Cached data fetchers
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def _cached_search(query: str, term_label: str) -> list[Course]:
    term = parse_term(term_label)
    courses = search_courses(query, cache_dir=CACHE_DIR)
    if term:
        courses = filter_courses_for_term(courses, term)
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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    st.set_page_config(
        page_title="Stanford Course NL Scheduler",
        page_icon="\U0001F393",  # 🎓
        layout="wide",
    )
    st.markdown(STANFORD_CSS, unsafe_allow_html=True)

    today = dt.date.today()
    ay_default = _guess_academic_year(today)
    q_default = _next_quarter(_default_quarter(today))

    # ----- Sidebar -----
    with st.sidebar:
        st.markdown("## \U0001F3AF Term")
        ay = st.text_input("Academic year", value=ay_default, help="e.g. 2025-2026")
        quarter = st.selectbox("Quarter", _quarters(), index=_quarters().index(q_default))
        term = Term(academic_year=ay.strip(), quarter=quarter)
        st.caption(f"Using term: **{term.label}**")

        st.divider()
        st.markdown("## \U0001F4CB Your Plan")

    conn = dbmod.connect(DB_PATH)

    with st.sidebar:
        _render_plan(conn, term)
        st.divider()
        if st.button("\U0001F5D1 Clear My Plan", type="secondary"):
            _clear_plan(conn, term)
            st.rerun()

    # ----- Main area -----
    st.markdown("# \U0001F393 Stanford Course Finder")

    # Welcome message on first load
    if "chat" not in st.session_state:
        st.session_state.chat = []
        st.markdown(
            '<div class="welcome-box">'
            "<h2>\U0001F44B Hi — I'm your Stanford course finder.</h2>"
            "<p>Tell me what you're looking for. Try things like:</p>"
            "<p><code>recommend ai courses</code> · <code>what courses are there about prompt engineering</code> · "
            "<code>tell me about CS 229</code> · <code>add CS 224N to my plan</code> · <code>show my plan</code></p>"
            "</div>",
            unsafe_allow_html=True,
        )

    # Chat history
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
                    "I can help you find Stanford courses! Try:\n"
                    "- **recommend ai courses** — curated GSB AI picks\n"
                    "- **find <topic>** — search for courses\n"
                    "- **tell me about CS 229** — course details\n"
                    "- **add CS 224N** — add to your plan\n"
                    "- **drop CS 229** — remove from plan\n"
                    "- **show my plan** — view current plan"
                )

            elif act.type == "show_plan":
                st.write(f"Your plan for {term.label}:")
                _render_plan(conn, term)

            elif act.type == "recommend":
                st.write(f"AI-centric recommendations for **{term.label}**:")
                with st.spinner("Searching ExploreCourses..."):
                    recs = _cached_recommend(term.label)
                if not recs:
                    st.info("No recommendations found for that term. Try changing academic year/quarter.")
                else:
                    # Split by tier
                    tier1 = [c for c in recs if get_tier(c) == 1]
                    tier2 = [c for c in recs if get_tier(c) == 2]
                    others = [c for c in recs if get_tier(c) is None]

                    if tier1:
                        st.markdown("### \U0001F31F Tier 1: Core AI")
                        for c in tier1:
                            with st.expander(f"{_subject_emoji(c.subject)} {c.course_id} — {c.title}", expanded=False):
                                _render_course_card(c, term, conn, show_blurb=True)

                    if tier2:
                        st.markdown("### \U0001F4D8 Tier 2: Strategy & Policy")
                        for c in tier2:
                            with st.expander(f"{_subject_emoji(c.subject)} {c.course_id} — {c.title}", expanded=False):
                                _render_course_card(c, term, conn, show_blurb=True)

                    if others:
                        st.markdown("### \U0001F50D Other Relevant Courses")
                        for c in others:
                            with st.expander(f"{_subject_emoji(c.subject)} {c.course_id} — {c.title}", expanded=False):
                                _render_course_card(c, term, conn)

            elif act.type == "info" and act.subject and act.code:
                q = f"{act.subject}{act.code}"
                st.write(f"Looking up **{act.subject} {act.code}**...")
                with st.spinner("Fetching course info..."):
                    courses = _cached_search(q, term.label)
                exact = [c for c in courses if c.subject == act.subject and c.code == act.code]
                if exact:
                    _render_course_info(exact[0], term, conn)
                elif courses:
                    st.warning(f"Couldn't find an exact match for {act.subject} {act.code}. Here are close results:")
                    for c in courses[:5]:
                        with st.expander(f"{_subject_emoji(c.subject)} {c.course_id} — {c.title}", expanded=False):
                            _render_course_card(c, term, conn)
                else:
                    st.warning(f"No results found for {act.subject} {act.code}. It may not be offered in {term.label}.")

            elif act.type == "add" and act.subject and act.code:
                q = f"{act.subject}{act.code}"
                st.write(f"Searching for **{act.subject} {act.code}** in {term.label}...")
                with st.spinner("Searching..."):
                    courses = _cached_search(q, term.label)
                exact = [c for c in courses if c.subject == act.subject and c.code == act.code]
                picks = exact or courses
                if not picks:
                    st.warning("No matches found.")
                else:
                    for c in picks[:5]:
                        with st.expander(f"{_subject_emoji(c.subject)} {c.course_id} — {c.title}", expanded=True):
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
                with st.spinner("Searching ExploreCourses..."):
                    courses = _cached_search(query, term.label)
                if not courses:
                    st.warning("No results.")
                else:
                    for c in courses[:30]:
                        with st.expander(f"{_subject_emoji(c.subject)} {c.course_id} — {c.title}", expanded=False):
                            _render_course_card(c, term, conn)
                    if len(courses) > 30:
                        st.caption(f"Showing top 30 of {len(courses)} results.")


if __name__ == "__main__":
    main()
