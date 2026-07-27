"""Минимальный событийный сценарий с реактивными агентами."""

from __future__ import annotations

import argparse
import json
import random


class ReactiveAgent:
    def __init__(self, name: str, skill: str) -> None:
        self.name = name
        self.skill = skill

    def act(self, event: dict[str, object]) -> str:
        if event["kind"] == self.skill:
            return "handle"
        if int(event["priority"]) >= 3:
            return "escalate"
        return "ignore"


def run(seed: int = 42, events: int = 8) -> dict[str, object]:
    rng = random.Random(seed)
    agents = [
        ReactiveAgent("agent-a", "sensor"),
        ReactiveAgent("agent-b", "network"),
        ReactiveAgent("agent-c", "compute"),
    ]
    kinds = ["sensor", "network", "compute", "unknown"]
    log: list[dict[str, object]] = []
    for event_id in range(events):
        event = {
            "id": event_id,
            "kind": rng.choice(kinds),
            "priority": rng.randint(1, 3),
        }
        actions = {agent.name: agent.act(event) for agent in agents}
        log.append({"event": event, "actions": actions})
    handled = sum("handle" in item["actions"].values() for item in log)
    escalated = sum("escalate" in item["actions"].values() for item in log)
    return {
        "seed": seed,
        "events": events,
        "handled_events": handled,
        "events_with_escalation": escalated,
        "log": log,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--events", type=int, default=8)
    args = parser.parse_args()
    print(json.dumps(run(args.seed, args.events), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
