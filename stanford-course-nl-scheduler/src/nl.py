from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, Optional

from .models import Term


ActionType = Literal["search", "add", "remove", "recommend", "show_plan", "help", "info"]


@dataclass(frozen=True)
class NLAction:
    type: ActionType
    query: Optional[str] = None
    subject: Optional[str] = None
    code: Optional[str] = None


# Matches course IDs like CS 229, MS&E 338, STATS 315A
COURSE_ID_RE = re.compile(r"\b([A-Z&]{2,})(?:\s*)(\d+[A-Z]?)\b")


def _extract_course_id(msg: str) -> tuple[Optional[str], Optional[str]]:
    """Extract subject and code from a message."""
    m = COURSE_ID_RE.search(msg.upper())
    if m:
        return m.group(1), m.group(2)
    return None, None


def parse(message: str) -> NLAction:
    msg = (message or "").strip()
    low = msg.lower()

    if not msg:
        return NLAction("help")

    if low in {"help", "?", "h"} or "what can you do" in low:
        return NLAction("help")

    # --- Recommend intent ---
    if any(kw in low for kw in ("recommend", "suggest", "what should i take",
                                  "what courses should", "best courses")):
        return NLAction("recommend")

    # --- Show plan intent ---
    if ("show" in low or "view" in low or "list" in low) and \
       any(w in low for w in ("plan", "schedule", "my courses")):
        return NLAction("show_plan")

    # --- Info intent: "tell me about CS 229", "what is CS 224N", "how many units is CS 229" ---
    info_patterns = [
        r"tell me about",
        r"what is",
        r"what are",
        r"how many units",
        r"details (?:for|on|about)",
        r"info (?:for|on|about)",
        r"describe",
        r"show me details",
    ]
    for pat in info_patterns:
        if re.search(pat, low):
            subj, code = _extract_course_id(msg)
            if subj and code:
                return NLAction("info", subject=subj, code=code)
            # If no course ID, treat as search with the query
            q = re.sub(pat, "", low, count=1).strip()
            if q:
                return NLAction("search", query=q)

    # --- Add intent ---
    add_patterns = [
        r"\badd\b", r"\bput\b.*\b(?:in|into|to)\b", r"\benroll\b",
        r"\bsign.{0,5}up\b", r"\bregister\b", r"\bi want to (?:take|add)\b",
        r"\binclude\b.*\b(?:in|into)\b",
    ]
    for pat in add_patterns:
        if re.search(pat, low):
            subj, code = _extract_course_id(msg)
            if subj and code:
                return NLAction("add", subject=subj, code=code)
            # fallback: treat as search
            q = re.sub(r"\b(?:add|put|enroll|register|include|sign\s*up)\b", "", low,
                       flags=re.I).strip()
            q = re.sub(r"\b(?:to|in|into|my|plan|schedule|for)\b", "", q).strip()
            if q:
                return NLAction("search", query=q)
            return NLAction("help")

    # --- Remove intent ---
    remove_patterns = [
        r"\bremove\b", r"\bdelete\b", r"\bdrop\b",
        r"\bdo not want\b", r"\bdon'?t want\b", r"\btake out\b",
        r"\bget rid of\b", r"\bcancel\b",
    ]
    for pat in remove_patterns:
        if re.search(pat, low):
            subj, code = _extract_course_id(msg)
            if subj and code:
                return NLAction("remove", subject=subj, code=code)
            return NLAction("show_plan")

    # --- Search with natural phrasing ---
    search_triggers = [
        (r"^(?:search|find)\s+(.+)", None),
        (r"^(?:look for|looking for)\s+(.+)", None),
        (r"what courses?\s+(?:are there\s+)?(?:about|on|for|in|related to)\s+(.+)", None),
        (r"i want to learn (?:about|more about)?\s*(.+)", None),
        (r"show me\s+(?:courses?\s+)?(?:about|on|for|in|related to)?\s*(.+)", None),
        (r"courses?\s+(?:about|on|for|in|related to)\s+(.+)", None),
        (r"(?:any|are there)\s+courses?\s+(?:about|on|for|in)\s+(.+)", None),
    ]
    for pat, _ in search_triggers:
        m = re.search(pat, low)
        if m:
            q = m.group(1).strip()
            # Clean trailing filler
            q = re.sub(r"\s*\?+\s*$", "", q)
            if q:
                return NLAction("search", query=q)

    # --- Bare course ID: "CS 229" ---
    subj, code = _extract_course_id(msg)
    if subj and code:
        clean = re.sub(r"[^a-z0-9&]", "", low)
        expected = (subj + code).lower()
        if clean == expected:
            # Just a course ID by itself — treat as info lookup
            return NLAction("info", subject=subj, code=code)
        # Course ID embedded in other text — search for it
        return NLAction("search", query=f"{subj} {code}")

    # Default: treat message as a search query.
    return NLAction("search", query=msg)
