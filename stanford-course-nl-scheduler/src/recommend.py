from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from .explorecourses import filter_courses_for_term, search_courses
from .models import Course, Term


AI_KEYWORDS = [
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "neural",
    "language model",
    "large language model",
    "llm",
    "generative",
    "diffusion",
    "transformer",
    "natural language",
    "nlp",
    "computer vision",
    "reinforcement learning",
    "policy gradient",
    "representation learning",
    "foundation model",
    "prompt",
    "embedding",
    "causal",
    "bayesian",
    "optimization",
    "data mining",
]

# Heuristic: departments that tend to have the most "AI core" content.
CORE_AI_SUBJECTS = {
    "CS": 3.0,
    "STATS": 2.2,
    "EE": 2.0,
    "CME": 1.8,
    "MS&E": 1.4,
    "LINGUIST": 1.2,
    "SYMSYS": 1.1,
}

# Heuristic: subjects that are often useful to a business-school schedule (strategy/policy/ethics/ops).
GSB_ADJACENT_SUBJECTS = {
    "MS&E": 0.8,
    "LAW": 0.8,
    "COMM": 0.6,
    "PUBLPOL": 0.6,
    "ETHICS": 0.4,
    "HISTORY": 0.2,
    "PSYCH": 0.3,
}


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").lower()).strip()


def ai_score(course: Course) -> float:
    text = _norm(course.title + " " + course.description)

    score = 0.0
    for kw in AI_KEYWORDS:
        if kw in text:
            score += 1.0

    # Subject priors
    score *= CORE_AI_SUBJECTS.get(course.subject, 1.0)
    score += GSB_ADJACENT_SUBJECTS.get(course.subject, 0.0)

    # Slight boost for graduate-ish courses (very rough; numbers are not standardized across Stanford)
    try:
        num = int(re.match(r"(\d+)", course.code).group(1))
        if num >= 200:
            score += 0.3
    except Exception:
        pass

    return score


def recommend_for_term(term: Term, *, cache_dir: Path, limit: int = 15) -> list[Course]:
    # Keep requests small: do a handful of broad searches, then score/rank locally.
    queries = [
        "machine learning",
        "deep learning",
        "large language model",
        "generative",
        "artificial intelligence",
        "data science",
    ]

    seen: dict[tuple[str, str, str], Course] = {}
    for q in queries:
        for c in search_courses(q, cache_dir=cache_dir):
            seen[(c.year, c.subject, c.code)] = c

    candidates = filter_courses_for_term(seen.values(), term)
    ranked = sorted(candidates, key=ai_score, reverse=True)

    # Drop obvious false-positives by score threshold.
    pruned = [c for c in ranked if ai_score(c) >= 4.0]

    return pruned[:limit]
