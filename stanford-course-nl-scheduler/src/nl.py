from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, Optional

from .models import Term


ActionType = Literal["search", "add", "remove", "recommend", "show_plan", "help"]


@dataclass(frozen=True)
class NLAction:
    type: ActionType
    query: Optional[str] = None
    subject: Optional[str] = None
    code: Optional[str] = None


COURSE_ID_RE = re.compile(r"\b([A-Z&]{2,})(?:\s*)(\d+[A-Z]?)\b")


def parse(message: str) -> NLAction:
    msg = (message or "").strip()
    low = msg.lower()

    if not msg:
        return NLAction("help")

    if low in {"help", "?", "h"} or "what can you do" in low:
        return NLAction("help")

    if "recommend" in low or "suggest" in low:
        return NLAction("recommend")

    if "show" in low and ("plan" in low or "schedule" in low or "my courses" in low):
        return NLAction("show_plan")

    if low.startswith("search ") or low.startswith("find "):
        return NLAction("search", query=msg.split(" ", 1)[1].strip())

    if "add" in low:
        # e.g. "add CS 229" or "add cs229"
        m = COURSE_ID_RE.search(msg.upper())
        if m:
            return NLAction("add", subject=m.group(1), code=m.group(2))
        # fallback: treat as search query and let UI offer add buttons
        q = re.sub(r"\badd\b", "", msg, flags=re.I).strip()
        return NLAction("search", query=q)

    if "remove" in low or "delete" in low or "drop" in low:
        m = COURSE_ID_RE.search(msg.upper())
        if m:
            return NLAction("remove", subject=m.group(1), code=m.group(2))
        return NLAction("show_plan")

    # Default: treat message as a search query.
    m = COURSE_ID_RE.search(msg.upper())
    if m and msg.replace(" ", "") == (m.group(1) + m.group(2)):
        return NLAction("search", query=f"{m.group(1)}{m.group(2)}")

    return NLAction("search", query=msg)
