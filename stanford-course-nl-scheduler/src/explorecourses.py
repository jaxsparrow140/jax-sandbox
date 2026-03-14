from __future__ import annotations

import hashlib
import os
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import asdict
from pathlib import Path
from typing import Iterable, Optional

import requests

from .models import Course, Section, Term


EXPLORECOURSES_XML_SEARCH = "https://explorecourses.stanford.edu/search"


def _cache_key(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def _read_cache(cache_dir: Path, key: str, max_age_s: int) -> Optional[str]:
    p = cache_dir / f"{key}.xml"
    if not p.exists():
        return None
    age = time.time() - p.stat().st_mtime
    if age > max_age_s:
        return None
    return p.read_text(encoding="utf-8", errors="ignore")


def _write_cache(cache_dir: Path, key: str, text: str) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    p = cache_dir / f"{key}.xml"
    p.write_text(text, encoding="utf-8")


def _normalize_ws(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def parse_term(term_str: str) -> Optional[Term]:
    term_str = _normalize_ws(term_str)
    m = re.match(r"^(\d{4}-\d{4})\s+(Autumn|Winter|Spring|Summer)$", term_str)
    if not m:
        return None
    return Term(academic_year=m.group(1), quarter=m.group(2))


def course_url(subject: str, code: str, academic_year: Optional[str] = None) -> str:
    # ExploreCourses doesn't expose a stable public course permalink for every view,
    # so we link to a pre-filled search.
    q = requests.utils.quote(f"{subject} {code}")
    if academic_year:
        ay = requests.utils.quote(academic_year)
        return f"https://explorecourses.stanford.edu/search?view=catalog&academicYear={ay}&q={q}"
    return f"https://explorecourses.stanford.edu/search?view=catalog&q={q}"


def fetch_xml(query: str, *, cache_dir: Path, cache_max_age_s: int = 60 * 60 * 12) -> str:
    q = query.strip()
    url = f"{EXPLORECOURSES_XML_SEARCH}?view=xml&q={requests.utils.quote(q)}"

    key = _cache_key(url)
    cached = _read_cache(cache_dir, key, cache_max_age_s)
    if cached is not None:
        return cached

    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    text = resp.text
    _write_cache(cache_dir, key, text)
    return text


def search_courses(query: str, *, cache_dir: Path) -> list[Course]:
    xml_text = fetch_xml(query, cache_dir=cache_dir)
    root = ET.fromstring(xml_text)

    courses: list[Course] = []

    for c in root.findall(".//course"):
        year = _normalize_ws(c.findtext("year"))
        subject = _normalize_ws(c.findtext("subject"))
        code = _normalize_ws(c.findtext("code"))
        title = _normalize_ws(c.findtext("title"))
        desc = _normalize_ws(c.findtext("description"))

        sections: list[Section] = []
        for s in c.findall(".//sections/section"):
            sections.append(
                Section(
                    class_id=_normalize_ws(s.findtext("classId")),
                    term=_normalize_ws(s.findtext("term")),
                    subject=_normalize_ws(s.findtext("subject")) or subject,
                    code=_normalize_ws(s.findtext("code")) or code,
                    units=_normalize_ws(s.findtext("units")),
                    section_number=_normalize_ws(s.findtext("sectionNumber")),
                    component=_normalize_ws(s.findtext("component")),
                    instructors=_normalize_ws(s.findtext("instructors")),
                    notes=_normalize_ws(s.findtext("notes")),
                )
            )

        courses.append(
            Course(
                year=year,
                subject=subject,
                code=code,
                title=title,
                description=desc,
                sections=tuple(sections),
            )
        )

    # Deduplicate by (year, subject, code)
    uniq: dict[tuple[str, str, str], Course] = {}
    for course in courses:
        uniq[(course.year, course.subject, course.code)] = course

    return list(uniq.values())


def filter_courses_for_term(courses: Iterable[Course], term: Term) -> list[Course]:
    wanted = term.label
    out: list[Course] = []
    for c in courses:
        if any(s.term == wanted for s in c.sections):
            out.append(c)
    return out
