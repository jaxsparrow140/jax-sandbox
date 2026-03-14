from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Term:
    academic_year: str  # e.g. "2025-2026"
    quarter: str  # "Autumn" | "Winter" | "Spring" | "Summer"

    @property
    def label(self) -> str:
        return f"{self.academic_year} {self.quarter}"


@dataclass(frozen=True)
class Section:
    class_id: str
    term: str  # raw string from ExploreCourses, e.g. "2025-2026 Autumn"
    subject: str
    code: str
    units: str
    section_number: str
    component: str
    instructors: str
    notes: str


@dataclass(frozen=True)
class Course:
    year: str
    subject: str
    code: str
    title: str
    description: str

    # Sections are term-specific offerings.
    sections: tuple[Section, ...]

    @property
    def course_id(self) -> str:
        return f"{self.subject} {self.code}".strip()

    @property
    def short_title(self) -> str:
        return self.title.strip()

    def offered_terms(self) -> list[str]:
        terms = sorted({s.term for s in self.sections if s.term})
        return terms
