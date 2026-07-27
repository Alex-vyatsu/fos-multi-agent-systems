"""Детерминированный макет LLM-оркестратора с ответственным контуром."""

from __future__ import annotations

import json


BLOCKED_MARKERS = {"удали", "опубликуй персональные", "переведи деньги"}


def planner(request: str) -> dict[str, object]:
    return {
        "agent": "planner",
        "proposal": f"Подготовить план для запроса: {request}",
        "confidence": 0.7,
    }


def critic(proposal: dict[str, object]) -> dict[str, object]:
    lowered = str(proposal["proposal"]).lower()
    blocked = [marker for marker in BLOCKED_MARKERS if marker in lowered]
    return {
        "agent": "critic",
        "allowed": not blocked,
        "reasons": blocked or ["опасные маркеры не обнаружены"],
    }


def orchestrate(request: str, human_approved: bool = False) -> dict[str, object]:
    proposal = planner(request)
    review = critic(proposal)
    if not review["allowed"]:
        status = "blocked"
    elif human_approved:
        status = "approved_by_human"
    else:
        status = "awaiting_human_decision"
    return {
        "request": request,
        "proposal": proposal,
        "review": review,
        "status": status,
        "executed": False,
    }


def main() -> None:
    safe = orchestrate("составь план проверки репозитория")
    unsafe = orchestrate("удали исходные данные")
    print(json.dumps({"safe": safe, "unsafe": unsafe}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
