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
TERMINAL_STATES = {"completed", "failed", "canceled"}


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
    state: str = "submitted"
    messages: list[str] = field(default_factory=list)
    artifacts: list[dict[str, object]] = field(default_factory=list)


class ProtocolHarness:
    """Минимальный test harness для проверяемого protocol slice."""

    def __init__(self, cards: list[AgentCard], *, tool_available: bool = True) -> None:
        self.cards = {card.agent_id: card for card in cards}
        self.tool_available = tool_available
        self.tasks: dict[str, Task] = {}
        self.trace: list[dict[str, object]] = []
        self._effect_ledger: dict[str, dict[str, object]] = {}

    def _record(self, boundary: str, event: str, task_id: str, **details: object) -> None:
        self.trace.append(
            {
                "boundary": boundary,
                "event": event,
                "task_id": task_id,
                **details,
            }
        )

    def delegate(
        self,
        *,
        task_id: str,
        target_agent: str,
        capability: str,
        a2a_version: str = A2A_BASELINE,
    ) -> Task:
        if task_id in self.tasks:
            raise ContractError(f"повторный task_id: {task_id}")
        card = self.cards.get(target_agent)
        if card is None:
            raise ContractError(f"агент недоступен: {target_agent}")
        if a2a_version not in card.a2a_versions:
            raise ContractError(f"неподдерживаемая версия A2A: {a2a_version}")
        if capability not in card.capabilities:
            raise ContractError(f"возможность не объявлена: {capability}")

        task = Task(task_id=task_id, target_agent=target_agent, capability=capability)
        self.tasks[task_id] = task
        self._record("A2A", "task_submitted", task_id, version=a2a_version)
        task.state = "working"
        task.messages.append("задача принята исполнителем")
        self._record("A2A", "task_working", task_id, agent=target_agent)
        return task

    def cancel(self, task_id: str) -> Task:
        task = self.tasks[task_id]
        if task.state in TERMINAL_STATES:
            raise ContractError(f"нельзя отменить задачу в состоянии {task.state}")
        task.state = "canceled"
        self._record("A2A", "task_canceled", task_id)
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
        if grant.revoked:
            raise ContractError("полномочие отозвано")
        if grant.subject != task.target_agent:
            raise ContractError("subject полномочия не совпадает с исполнителем")
        if grant.audience != "request-catalog":
            raise ContractError("неверная audience полномочия")
        if grant.task_id != task_id:
            raise ContractError("полномочие выпущено для другой задачи")
        if grant.resource != resource:
            raise ContractError("полномочие выпущено для другого ресурса")
        if tool_name != "lookup_requests" or "requests:read" not in grant.scopes:
            raise ContractError("инструмент или scope не разрешён")
        if current_step > grant.expires_at_step:
            if task.state not in TERMINAL_STATES:
                task.state = "failed"
            self._record("MCP", "grant_expired", task_id, version=MCP_BASELINE)
            raise ContractError("истёк срок полномочия")

        # Идемпотентность не обходит авторизацию: даже повторный запрос должен
        # предъявить действующее, связанное с этой задачей полномочие.
        if effect_key in self._effect_ledger:
            artifact = self._effect_ledger[effect_key]
            self._record("MCP", "tool_replayed", task_id, effect_key=effect_key)
            return artifact
        if task.state != "working":
            raise ContractError(f"задача не допускает вызов инструмента: {task.state}")

        if not self.tool_available:
            task.state = "failed"
            self._record("MCP", "tool_unavailable", task_id, tool=tool_name)
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
        )
        self._record("A2A", "artifact_published", task_id, artifact_id=artifact["artifact_id"])
        return artifact


def default_card() -> AgentCard:
    return AgentCard(
        agent_id="request-analyst",
        owner="analytics-team",
        capabilities=frozenset({"summarize_requests"}),
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


def run_demo(*, tool_available: bool = True) -> dict[str, object]:
    harness = ProtocolHarness([default_card()], tool_available=tool_available)
    task = harness.delegate(
        task_id="task-001",
        target_agent="request-analyst",
        capability="summarize_requests",
    )
    error = None
    artifact = None
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
    return {
        "baselines": {"A2A": A2A_BASELINE, "MCP": MCP_BASELINE},
        "task_state": task.state,
        "artifact": artifact,
        "error": error,
        "trace": harness.trace,
        "claim_boundary": "semantic contract slice; wire-conformance not claimed",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--unavailable-tool", action="store_true")
    args = parser.parse_args()
    print(
        json.dumps(
            run_demo(tool_available=not args.unavailable_tool),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
