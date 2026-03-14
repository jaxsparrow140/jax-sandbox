from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Any, Optional

from .models import Course, Section, Term
from .explorecourses import course_url


SCHEMA = """
CREATE TABLE IF NOT EXISTS planned_courses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  academic_year TEXT NOT NULL,
  quarter TEXT NOT NULL,
  subject TEXT NOT NULL,
  code TEXT NOT NULL,
  title TEXT NOT NULL,
  units TEXT,
  component TEXT,
  instructors TEXT,
  source_url TEXT,
  notes TEXT,
  added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(academic_year, quarter, subject, code)
);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def add_course(
    conn: sqlite3.Connection,
    *,
    term: Term,
    course: Course,
    section: Optional[Section] = None,
    notes: Optional[str] = None,
) -> bool:
    sec = section
    src_url = course_url(course.subject, course.code, academic_year=term.academic_year)

    try:
        conn.execute(
            """
            INSERT OR IGNORE INTO planned_courses (
              academic_year, quarter, subject, code, title, units, component, instructors, source_url, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                term.academic_year,
                term.quarter,
                course.subject,
                course.code,
                course.title,
                (sec.units if sec else None),
                (sec.component if sec else None),
                (sec.instructors if sec else None),
                src_url,
                notes,
            ),
        )
        conn.commit()
    except sqlite3.Error:
        return False

    # If ignored due to UNIQUE, rowcount == 0
    return conn.total_changes > 0


def remove_course(conn: sqlite3.Connection, *, term: Term, subject: str, code: str) -> bool:
    cur = conn.execute(
        "DELETE FROM planned_courses WHERE academic_year=? AND quarter=? AND subject=? AND code=?",
        (term.academic_year, term.quarter, subject, code),
    )
    conn.commit()
    return cur.rowcount > 0


def list_plan(conn: sqlite3.Connection, *, term: Term) -> list[dict[str, Any]]:
    cur = conn.execute(
        """
        SELECT academic_year, quarter, subject, code, title, units, component, instructors, source_url, notes, added_at
        FROM planned_courses
        WHERE academic_year=? AND quarter=?
        ORDER BY subject, CAST(REPLACE(code, 'A','') AS TEXT), code
        """,
        (term.academic_year, term.quarter),
    )
    return [dict(r) for r in cur.fetchall()]
