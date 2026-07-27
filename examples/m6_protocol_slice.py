"""Учебная модель семантики A2A/MCP, а не сетевая реализация протоколов.

Модель разделяет межагентную задачу (A2A) и вызов инструмента (MCP), проверяет
возможность до делегирования, жизненный цикл, ограниченное полномочие,
идемпотентность и отказные сценарии. Она не подтверждает wire-conformance.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field


A2A_BASELINE = "1.0.0"
MCP_BASELINE = "2025-11-25"
TRACE_SCHEMA_VERSION = "1.0"
POLICY_BUNDLE_VERSION = "defense-policy-1.0"
TOOL_VERSION = "request-catalog-1.0"
DATA_VERSION = "requests-demo-1.0"
MODEL_VERSION = "deterministic-no-llm"
TERMINAL_STATES = {"completed", "failed", "canceled"}
PATTERNS = {"orchestrator", "reviewed_pipeline"}

EVENT_LATENCY_MS = {
    "task_submitted": 2,
    "task_working": 1,
    "tool_completed": 4,
    "tool_replayed": 1,
    "artifact_published": 1,
    "review_completed": 3,
    "task_canceled": 1,
    "grant_expired": 1,
    "tool_unavailable": 2,
    "request_rejected": 1,
}


class ContractError(RuntimeError):
    """Проверяемое отклонение контракта или полномочия."""


@dataclass(frozen=True)
class AgentCard:
    agent_id: str
    owner: str
    capabilities: frozenset[str]
    a2a_versions: frozenset[str] = frozenset({A2A_BASELINE})


@dataclass(frozen=True)
class Grant:
    subject: str
    audience: str
    scopes: frozenset[str]
    resource: str
    task_id: str
    expires_at_step: int
    revoked: bool = False


@dataclass
class Task:
    task_id: str
    target_agent: str
    capability: str
    parent_task_id: str | None = None
    state: str = "submitted"
    messages: list[str] = field(default_factory=list)
    artifacts: list[dict[str, object]] = field(default_factory=list)


class ProtocolHarness:
    """Минимальный test harness для проверяемого protocol slice."""

    def __init__(
        self,
        cards: list[AgentCard],
        *,
        tool_available: bool = True,
        interaction_id: str = "interaction-001",
    ) -> None:
        self.cards = {card.agent_id: card for card in cards}
        self.tool_available = tool_available
        self.interaction_id = interaction_id
        self.tasks: dict[str, Task] = {}
        self.trace: list[dict[str, object]] = []
        self._effect_ledger: dict[str, dict[str, object]] = {}

    def _record(self, boundary: str, event: str, task_id: str, **details: object) -> None:
        sequence = len(self.trace) + 1
        self.trace.append(
            {
                "trace_schema_version": TRACE_SCHEMA_VERSION,
                "interaction_id": self.interaction_id,
                "sequence": sequence,
                "boundary": boundary,
                "event": event,
                "task_id": task_id,
                "latency_ms": EVENT_LATENCY_MS[event],
                "external_cost_usd": 0.0,
                **details,
            }
        )

    def _reject(
        self,
        *,
        task_id: str,
        reason: str,
        boundary: str = "POLICY",
        **details: object,
    ) -> None:
        self._record(
            boundary,
            "request_rejected",
            task_id,
            policy_version=POLICY_BUNDLE_VERSION,
            policy_decision_id=f"deny-{task_id}-{len(self.trace) + 1}",
            reason=reason,
            **details,
        )
        raise ContractError(reason)

    def delegate(
        self,
        *,
        task_id: str,
        target_agent: str,
        capability: str,
        a2a_version: str = A2A_BASELINE,
        parent_task_id: str | None = None,
    ) -> Task:
        if task_id in self.tasks:
            self._reject(task_id=task_id, reason=f"повторный task_id: {task_id}")
        card = self.cards.get(target_agent)
        if card is None:
            self._reject(
                task_id=task_id,
                reason=f"агент недоступен: {target_agent}",
                target_agent=target_agent,
            )
        if a2a_version not in card.a2a_versions:
            self._reject(
                task_id=task_id,
                reason=f"неподдерживаемая версия A2A: {a2a_version}",
                target_agent=target_agent,
                requested_version=a2a_version,
            )
        if capability not in card.capabilities:
            self._reject(
                task_id=task_id,
                reason=f"возможность не объявлена: {capability}",
                target_agent=target_agent,
                capability=capability,
            )

        task = Task(
            task_id=task_id,
            target_agent=target_agent,
            capability=capability,
            parent_task_id=parent_task_id,
        )
        self.tasks[task_id] = task
        self._record(
            "A2A",
            "task_submitted",
            task_id,
            parent_task_id=parent_task_id,
            agent_id=target_agent,
            agent_owner=card.owner,
            capability=capability,
            version=a2a_version,
        )
        task.state = "working"
        task.messages.append("задача принята исполнителем")
        self._record("A2A", "task_working", task_id, agent_id=target_agent)
        return task

    def cancel(self, task_id: str) -> Task:
        task = self.tasks[task_id]
        if task.state in TERMINAL_STATES:
            self._reject(
                task_id=task_id,
                reason=f"нельзя отменить задачу в состоянии {task.state}",
                state=task.state,
            )
        task.state = "canceled"
        self._record("A2A", "task_canceled", task_id, agent_id=task.target_agent)
        return task

    def call_tool(
        self,
        *,
        task_id: str,
        grant: Grant,
        tool_name: str,
        resource: str,
        current_step: int,
        effect_key: str,
    ) -> dict[str, object]:
        task = self.tasks[task_id]
        tool_call_id = f"tool-{effect_key.replace(':', '-')}"
        if grant.revoked:
            self._reject(task_id=task_id, reason="полномочие отозвано")
        if grant.subject != task.target_agent:
            self._reject(
                task_id=task_id,
                reason="subject полномочия не совпадает с исполнителем",
            )
        if grant.audience != "request-catalog":
            self._reject(task_id=task_id, reason="неверная audience полномочия")
        if grant.task_id != task_id:
            self._reject(
                task_id=task_id,
                reason="полномочие выпущено для другой задачи",
            )
        if grant.resource != resource:
            self._reject(
                task_id=task_id,
                reason="полномочие выпущено для другого ресурса",
            )
        if tool_name != "lookup_requests" or "requests:read" not in grant.scopes:
            self._reject(
                task_id=task_id,
                reason="инструмент или scope не разрешён",
                tool_call_id=tool_call_id,
                tool_name=tool_name,
            )
        if current_step > grant.expires_at_step:
            if task.state not in TERMINAL_STATES:
                task.state = "failed"
            self._record(
                "MCP",
                "grant_expired",
                task_id,
                version=MCP_BASELINE,
                tool_call_id=tool_call_id,
                agent_id=task.target_agent,
                policy_version=POLICY_BUNDLE_VERSION,
                error="истёк срок полномочия",
            )
            raise ContractError("истёк срок полномочия")

        # Идемпотентность не обходит авторизацию: даже повторный запрос должен
        # предъявить действующее, связанное с этой задачей полномочие.
        if effect_key in self._effect_ledger:
            artifact = self._effect_ledger[effect_key]
            self._record(
                "MCP",
                "tool_replayed",
                task_id,
                effect_key=effect_key,
                tool_call_id=tool_call_id,
                artifact_id=artifact["artifact_id"],
                agent_id=task.target_agent,
            )
            return artifact
        if task.state != "working":
            self._reject(
                task_id=task_id,
                reason=f"задача не допускает вызов инструмента: {task.state}",
                state=task.state,
            )

        if not self.tool_available:
            task.state = "failed"
            self._record(
                "MCP",
                "tool_unavailable",
                task_id,
                tool=tool_name,
                tool_call_id=tool_call_id,
                tool_version=TOOL_VERSION,
                agent_id=task.target_agent,
                error="инструмент недоступен",
            )
            raise ContractError("инструмент недоступен")

        artifact = {
            "artifact_id": f"artifact-{task_id}",
            "kind": "request-summary",
            "request_count": 3,
        }
        self._effect_ledger[effect_key] = artifact
        task.artifacts.append(artifact)
        task.state = "completed"
        self._record(
            "MCP",
            "tool_completed",
            task_id,
            version=MCP_BASELINE,
            effect_key=effect_key,
            tool_call_id=tool_call_id,
            tool_name=tool_name,
            tool_version=TOOL_VERSION,
            data_version=DATA_VERSION,
            policy_version=POLICY_BUNDLE_VERSION,
            policy_decision_id=f"allow-{task_id}-read",
            agent_id=task.target_agent,
            artifact_id=artifact["artifact_id"],
        )
        self._record(
            "A2A",
            "artifact_published",
            task_id,
            artifact_id=artifact["artifact_id"],
            agent_id=task.target_agent,
        )
        return artifact

    def complete_review(
        self,
        *,
        task_id: str,
        source_artifact: dict[str, object],
        approved: bool,
    ) -> dict[str, object]:
        task = self.tasks[task_id]
        if task.capability != "review_summary":
            self._reject(
                task_id=task_id,
                reason="задача не объявляет capability review_summary",
            )
        if task.state != "working":
            self._reject(
                task_id=task_id,
                reason=f"review недоступен в состоянии {task.state}",
            )
        review_artifact = {
            "artifact_id": f"review-{task_id}",
            "kind": "review-decision",
            "source_artifact_id": source_artifact["artifact_id"],
            "approved": approved,
        }
        task.artifacts.append(review_artifact)
        task.state = "completed"
        self._record(
            "A2A",
            "review_completed",
            task_id,
            parent_task_id=task.parent_task_id,
            agent_id=task.target_agent,
            source_artifact_id=source_artifact["artifact_id"],
            artifact_id=review_artifact["artifact_id"],
            policy_version=POLICY_BUNDLE_VERSION,
            policy_decision_id=f"review-{task_id}",
            approved=approved,
        )
        return review_artifact


def default_card() -> AgentCard:
    return AgentCard(
        agent_id="request-analyst",
        owner="analytics-team",
        capabilities=frozenset({"summarize_requests"}),
    )


def default_reviewer_card() -> AgentCard:
    return AgentCard(
        agent_id="quality-reviewer",
        owner="quality-team",
        capabilities=frozenset({"review_summary"}),
    )


def default_grant(task_id: str, *, expires_at_step: int = 5) -> Grant:
    return Grant(
        subject="request-analyst",
        audience="request-catalog",
        scopes=frozenset({"requests:read"}),
        resource="requests/demo",
        task_id=task_id,
        expires_at_step=expires_at_step,
    )


def trace_metrics(trace: list[dict[str, object]]) -> dict[str, object]:
    return {
        "event_count": len(trace),
        "a2a_event_count": sum(event["boundary"] == "A2A" for event in trace),
        "mcp_event_count": sum(event["boundary"] == "MCP" for event in trace),
        "model_event_count": sum(event["boundary"] == "MODEL" for event in trace),
        "policy_event_count": sum(event["boundary"] == "POLICY" for event in trace),
        "latency_budget_ms": sum(int(event["latency_ms"]) for event in trace),
        "external_cost_usd": round(
            sum(float(event["external_cost_usd"]) for event in trace),
            4,
        ),
        "error_count": sum(
            event["event"] in {"request_rejected", "grant_expired", "tool_unavailable"}
            for event in trace
        ),
    }


def run_demo(
    *,
    tool_available: bool = True,
    pattern: str = "orchestrator",
    interaction_id: str = "interaction-001",
) -> dict[str, object]:
    if pattern not in PATTERNS:
        raise ValueError(f"неизвестный паттерн: {pattern}")
    harness = ProtocolHarness(
        [default_card(), default_reviewer_card()],
        tool_available=tool_available,
        interaction_id=interaction_id,
    )
    task = harness.delegate(
        task_id="task-001",
        target_agent="request-analyst",
        capability="summarize_requests",
    )
    error = None
    artifact = None
    review_artifact = None
    review_task = None
    try:
        artifact = harness.call_tool(
            task_id=task.task_id,
            grant=default_grant(task.task_id),
            tool_name="lookup_requests",
            resource="requests/demo",
            current_step=1,
            effect_key="task-001:lookup",
        )
    except ContractError as exc:
        error = str(exc)
    if artifact is not None and pattern == "reviewed_pipeline":
        review_task = harness.delegate(
            task_id="task-002",
            target_agent="quality-reviewer",
            capability="review_summary",
            parent_task_id=task.task_id,
        )
        review_artifact = harness.complete_review(
            task_id=review_task.task_id,
            source_artifact=artifact,
            approved=True,
        )
    required_trace_fields = {
        "trace_schema_version",
        "interaction_id",
        "sequence",
        "boundary",
        "event",
        "task_id",
        "latency_ms",
        "external_cost_usd",
    }
    trace_complete = bool(harness.trace) and all(
        required_trace_fields <= event.keys() for event in harness.trace
    )
    review_complete = pattern == "orchestrator" or (
        review_task is not None and review_task.state == "completed"
    )
    return {
        "pattern": pattern,
        "baselines": {"A2A": A2A_BASELINE, "MCP": MCP_BASELINE},
        "versions": {
            "trace_schema": TRACE_SCHEMA_VERSION,
            "policy": POLICY_BUNDLE_VERSION,
            "tool": TOOL_VERSION,
            "data": DATA_VERSION,
            "model": MODEL_VERSION,
        },
        "task_state": task.state,
        "review_state": review_task.state if review_task is not None else "not_required",
        "artifact": artifact,
        "review_artifact": review_artifact,
        "error": error,
        "trace": harness.trace,
        "metrics": trace_metrics(harness.trace),
        "quality": {
            "trace_complete": trace_complete,
            "a2a_mcp_separated": all(
                event["boundary"] in {"A2A", "MCP", "POLICY"}
                for event in harness.trace
            ),
            "independent_review": pattern == "reviewed_pipeline",
            "review_complete": review_complete,
        },
        "approval_state": "awaiting_human_decision",
        "claim_boundary": "semantic contract slice; wire-conformance not claimed",
    }


def compare_patterns(*, tool_available: bool = True) -> dict[str, object]:
    variants = {
        pattern: run_demo(
            tool_available=tool_available,
            pattern=pattern,
            interaction_id=f"comparison-{pattern}",
        )
        for pattern in sorted(PATTERNS)
    }
    return {
        "variants": variants,
        "decision": {
            "low_risk": "orchestrator",
            "high_risk": "reviewed_pipeline",
            "rationale": (
                "reviewed_pipeline добавляет независимую проверку ценой "
                "дополнительных A2A-событий и latency budget"
            ),
        },
        "metric_boundary": (
            "latency_ms — детерминированный учебный budget; "
            "external_cost_usd = 0, потому что внешняя модель/API не вызывается"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--unavailable-tool", action="store_true")
    parser.add_argument("--pattern", choices=sorted(PATTERNS), default="orchestrator")
    parser.add_argument("--compare-patterns", action="store_true")
    args = parser.parse_args()
    result = (
        compare_patterns(tool_available=not args.unavailable_tool)
        if args.compare_patterns
        else run_demo(
            tool_available=not args.unavailable_tool,
            pattern=args.pattern,
        )
    )
    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
