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


# ---------------------------------------------------------------------------
# Curated GSB AI Courses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CuratedCourse:
    subject: str
    code: str
    search_query: str  # what to search for on ExploreCourses
    tier: int  # 1 or 2
    blurb: str  # why it's great for GSB + AI


GSB_AI_COURSES: list[CuratedCourse] = [
    # --- Tier 1: Core AI ---
    CuratedCourse("CS", "224N", "CS224N", 1,
                  "The gold standard NLP course — covers transformers, attention, and LLMs. Essential for anyone building with language AI."),
    CuratedCourse("CS", "229", "CS229", 1,
                  "Stanford's flagship ML course. Gives you the mathematical foundations to evaluate any AI system or vendor pitch."),
    CuratedCourse("CS", "231N", "CS231N", 1,
                  "Deep learning for vision — critical for understanding multimodal AI, image generation, and autonomous systems."),
    CuratedCourse("CS", "324", "CS324", 1,
                  "Dedicated LLM course covering architecture, training, deployment, and societal implications of large language models."),
    CuratedCourse("CS", "336", "CS336", 1,
                  "Build a language model from scratch — the deepest hands-on understanding you can get of how GPT-style models work."),
    CuratedCourse("CS", "472", "CS472", 1,
                  "AI for healthcare — a booming sector for GSB students interested in health-tech ventures and digital health strategy."),
    CuratedCourse("MS&E", "338", "MS&E 338 reinforcement learning", 1,
                  "RL from an engineering/decision-making perspective — perfect for understanding AI agents and autonomous decision systems."),
    CuratedCourse("MS&E", "348", "MS&E 348 AI society", 1,
                  "AI and society through the MS&E lens — governance, fairness, and societal impact. Key for responsible AI leadership."),
    CuratedCourse("MGTECON", "356", "MGTECON 356", 1,
                  "AI and the economy — understand macro/micro impacts of AI adoption, automation, and labor market shifts."),
    CuratedCourse("OIT", "367", "OIT 367", 1,
                  "AI and data analytics for operations — directly applicable to business strategy and operational decision-making."),
    CuratedCourse("CS", "221", "CS221", 1,
                  "The breadth AI course — search, logic, MDPs, ML. Provides the full conceptual map before you specialize."),
    CuratedCourse("CS", "234", "CS234", 1,
                  "Deep reinforcement learning — the theory behind recommendation engines, robotics, and game-playing AI."),
    CuratedCourse("CS", "330", "CS330", 1,
                  "Multi-task and meta learning — how to build AI systems that generalize across tasks with less data."),
    CuratedCourse("STATS", "315A", "STATS 315A", 1,
                  "Modern applied statistics focused on learning — bridges classical stats and ML for rigorous data-driven decisions."),
    CuratedCourse("STATS", "315B", "STATS 315B", 1,
                  "Data mining and applied ML — practical techniques for extracting insights from large business datasets."),
    CuratedCourse("CS", "238", "CS238", 1,
                  "Decision making under uncertainty — foundational for AI product managers and anyone deploying AI in high-stakes settings."),
    # --- Tier 2: Strategy & Policy ---
    CuratedCourse("MS&E", "339", "MS&E 339 AI strategy", 2,
                  "AI strategy from an MS&E perspective — directly relevant to business strategy and competitive advantage through AI."),
    CuratedCourse("LAW", "4390", "LAW 4390 AI", 2,
                  "AI law and policy — essential for understanding regulatory landscape, liability, and IP issues around AI products."),
    CuratedCourse("COMM", "267D", "computational communication", 2,
                  "Computational methods for communication research — useful for understanding AI in media, marketing, and public opinion."),
    CuratedCourse("PUBLPOL", "353", "PUBLPOL 353 technology", 2,
                  "Technology policy — the regulatory and political context every AI entrepreneur needs to navigate."),
    CuratedCourse("GSBGEN", "566", "GSBGEN 566 AI business", 2,
                  "AI in business — a GSB course specifically designed for MBAs wanting to leverage AI in their careers."),
]

# Quick lookup by (subject, code)
_CURATED_BY_ID: dict[tuple[str, str], CuratedCourse] = {
    (c.subject, c.code): c for c in GSB_AI_COURSES
}

COURSE_BLURBS: dict[tuple[str, str], str] = {
    (c.subject, c.code): c.blurb for c in GSB_AI_COURSES
}

COURSE_TIERS: dict[tuple[str, str], int] = {
    (c.subject, c.code): c.tier for c in GSB_AI_COURSES
}


def get_tier(course: Course) -> Optional[int]:
    return COURSE_TIERS.get((course.subject, course.code))


def get_blurb(course: Course) -> Optional[str]:
    return COURSE_BLURBS.get((course.subject, course.code))


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

    # Big boost for curated courses
    curated = _CURATED_BY_ID.get((course.subject, course.code))
    if curated:
        score += 50 if curated.tier == 1 else 30

    return score


def recommend_for_term(term: Term, *, cache_dir: Path, limit: int = 30) -> list[Course]:
    seen: dict[tuple[str, str, str], Course] = {}

    # First: search for each curated course specifically
    for cc in GSB_AI_COURSES:
        try:
            results = search_courses(cc.search_query, cache_dir=cache_dir)
            for c in results:
                seen[(c.year, c.subject, c.code)] = c
        except Exception:
            pass

    # Then: supplement with broad keyword searches
    broad_queries = [
        "machine learning",
        "deep learning",
        "large language model",
        "generative",
        "artificial intelligence",
        "data science",
    ]
    for q in broad_queries:
        try:
            for c in search_courses(q, cache_dir=cache_dir):
                seen[(c.year, c.subject, c.code)] = c
        except Exception:
            pass

    candidates = filter_courses_for_term(seen.values(), term)
    ranked = sorted(candidates, key=ai_score, reverse=True)

    # Keep curated courses even if their ai_score is lower; filter non-curated by threshold
    pruned = []
    for c in ranked:
        if get_tier(c) is not None:
            pruned.append(c)
        elif ai_score(c) >= 4.0:
            pruned.append(c)

    return pruned[:limit]
