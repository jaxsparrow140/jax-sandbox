"""
Natural language search engine for Stanford courses.
Uses keyword extraction + fuzzy matching.
"""

import re
from rapidfuzz import fuzz, process


# Day name mappings for natural language queries
DAY_KEYWORDS = {
    "monday": "Mon", "mon": "Mon",
    "tuesday": "Tue", "tue": "Tue", "tues": "Tue",
    "wednesday": "Wed", "wed": "Wed",
    "thursday": "Thu", "thu": "Thu", "thurs": "Thu",
    "friday": "Fri", "fri": "Fri",
    "mwf": "Mon,Wed,Fri", "tth": "Tue,Thu",
}

# Stop words to filter out
STOP_WORDS = {
    "show", "me", "find", "search", "for", "the", "a", "an", "in", "on",
    "about", "what", "are", "is", "best", "good", "great", "top",
    "classes", "class", "courses", "course", "next", "quarter",
    "i", "want", "to", "take", "can", "you", "please", "any",
    "some", "with", "and", "or", "of", "that", "this", "my",
}

# Keyword expansions for common AI terms
TERM_EXPANSIONS = {
    "ai": ["artificial intelligence", "AI", "machine learning"],
    "ml": ["machine learning", "ML", "statistical learning"],
    "nlp": ["natural language processing", "NLP", "language", "text"],
    "cv": ["computer vision", "vision", "image"],
    "rl": ["reinforcement learning", "RL", "decision making"],
    "dl": ["deep learning", "neural network", "deep"],
    "llm": ["large language model", "LLM", "language model", "transformer", "GPT"],
    "llms": ["large language model", "LLM", "language model", "transformer"],
    "transformers": ["transformer", "attention", "language model", "GPT", "BERT"],
    "gans": ["generative adversarial", "GAN", "generative model"],
    "diffusion": ["diffusion model", "generative", "score-based"],
    "robotics": ["robot", "robotics", "autonomy", "autonomous"],
    "optimization": ["optimization", "convex", "gradient"],
    "stats": ["statistics", "statistical", "STATS"],
    "business": ["business", "management", "strategy", "GSB", "OIT", "STRAMGT"],
    "ethics": ["ethics", "ethical", "fairness", "bias", "responsible"],
    "finance": ["finance", "financial", "fintech", "trading"],
    "marketing": ["marketing", "customer", "segmentation", "pricing"],
}


def extract_query_parts(query: str) -> dict:
    """Extract keywords, day filters, and department filters from natural language."""
    query_lower = query.lower().strip()

    # Extract day filters
    day_filters = []
    for kw, day_abbr in DAY_KEYWORDS.items():
        if kw in query_lower.split():
            for d in day_abbr.split(","):
                if d not in day_filters:
                    day_filters.append(d)

    # Extract department filters
    dept_filters = []
    dept_pattern = re.findall(r'\b(CS|EE|MS&E|MSE|STATS|OIT|STRAMGT|GSBGEN|FINANCE|MKTG|MGTECON)\b', query, re.I)
    for d in dept_pattern:
        dept_filters.append(d.upper().replace("MSE", "MS&E"))

    # Extract course code patterns
    code_pattern = re.findall(r'\b([A-Z&]+\s*\d+\w*)\b', query, re.I)

    # Extract meaningful keywords
    words = re.findall(r'\b\w+\b', query_lower)
    keywords = []
    for w in words:
        if w in STOP_WORDS:
            continue
        if w in DAY_KEYWORDS:
            continue
        if w.upper() in [d.upper() for d in dept_pattern]:
            continue
        # Expand abbreviations
        if w in TERM_EXPANSIONS:
            keywords.extend(TERM_EXPANSIONS[w])
        else:
            keywords.append(w)

    return {
        "keywords": keywords,
        "day_filters": day_filters,
        "dept_filters": dept_filters,
        "code_patterns": [c.upper() for c in code_pattern],
    }


def score_course(course: dict, query_parts: dict) -> float:
    """Score a course against parsed query parts. Higher = better match."""
    score = 0.0
    keywords = query_parts["keywords"]

    if not keywords and not query_parts["code_patterns"]:
        return 0.0

    # Check code patterns (exact or fuzzy match)
    for pattern in query_parts["code_patterns"]:
        code_clean = course["code"].replace(" ", "").upper()
        pattern_clean = pattern.replace(" ", "").upper()
        if pattern_clean in code_clean or code_clean in pattern_clean:
            score += 100
        elif fuzz.partial_ratio(pattern_clean, code_clean) > 80:
            score += 60

    # Build searchable text
    search_text = f"{course['code']} {course['title']} {course['description']} {course['instructor']} {course['department']}"

    # Keyword matching
    for kw in keywords:
        kw_lower = kw.lower()

        # Exact substring match in title (high value)
        if kw_lower in course["title"].lower():
            score += 30

        # Exact substring match in description
        if kw_lower in course["description"].lower():
            score += 15

        # Exact substring in code or department
        if kw_lower in course["code"].lower() or kw_lower in course["department"].lower():
            score += 25

        # Fuzzy match against title
        title_score = fuzz.partial_ratio(kw_lower, course["title"].lower())
        if title_score > 70:
            score += title_score * 0.2

        # Fuzzy match against description
        desc_score = fuzz.partial_ratio(kw_lower, course["description"].lower())
        if desc_score > 70:
            score += desc_score * 0.1

    # Department filter bonus
    for dept in query_parts["dept_filters"]:
        if course["department"].upper() == dept.upper():
            score += 20

    # Day filter - check if course is on requested days
    for day in query_parts["day_filters"]:
        if day in course.get("schedule", ""):
            score += 15

    return score


def search_courses(query: str, courses: list[dict], limit: int = 20) -> list[dict]:
    """Search courses using natural language query."""
    if not query.strip():
        return courses[:limit]

    query_parts = extract_query_parts(query)

    # Score all courses
    scored = []
    for course in courses:
        s = score_course(course, query_parts)
        if s > 0:
            scored.append((course, s))

    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)

    # Apply day filter as hard constraint if specified
    if query_parts["day_filters"]:
        filtered = []
        for course, s in scored:
            schedule = course.get("schedule", "")
            if any(day in schedule for day in query_parts["day_filters"]):
                filtered.append(course)
        return filtered[:limit]

    return [c for c, s in scored[:limit]]
