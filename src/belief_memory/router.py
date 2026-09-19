"""Content-only functional routing."""
from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol
from .models import Experience, FunctionalType

@dataclass(frozen=True)
class RouteResult:
    functional_type: FunctionalType
    confidence: float = 1.0
    supported: bool = True
    summarized_content: str | None = None

class Router(Protocol):
    def route(self, experience: Experience) -> RouteResult: ...

class CallableRouter:
    def __init__(self, classifier: Callable[[str], RouteResult]):
        self._classifier = classifier
    def route(self, experience: Experience) -> RouteResult:
        return self._classifier(experience.content)

class RuleBasedRouter:
    """Dependency-free example router; use an LLM-backed Router for production."""
    def route(self, experience: Experience) -> RouteResult:
        text = experience.content.lower().strip()
        if text.endswith("?") or text.startswith(("please ", "can you ", "could you ", "remind me")):
            return RouteResult(FunctionalType.EVENT, summarized_content=experience.content)
        if any(x in text for x in ("i like ", "i love ", "i prefer ", "i dislike ", "i hate ", "my favorite ")):
            return RouteResult(FunctionalType.PERSONAL_PREFERENCE, summarized_content=experience.content)
        if any(x in text for x in ("my ", "our ", "i live ", "i work ", "my partner", "my manager")):
            return RouteResult(FunctionalType.RELATIONAL_FACT, summarized_content=experience.content)
        if any(x in text for x in ("always ", "never ", "from now on", "please always", "please never")):
            return RouteResult(FunctionalType.GENERAL_RULE, summarized_content=experience.content)
        return RouteResult(FunctionalType.EXTERNAL_FACT, summarized_content=experience.content)
