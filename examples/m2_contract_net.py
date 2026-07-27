"""Упрощённый Contract Net с воспроизводимыми заявками агентов."""

from __future__ import annotations

import argparse
import json
import random


def allocate(seed: int = 42, task_count: int = 8) -> dict[str, object]:
    rng = random.Random(seed)
    agents = {
        "agent-a": {"sensor": 1.0, "network": 2.0, "compute": 2.5},
        "agent-b": {"sensor": 2.0, "network": 1.0, "compute": 2.0},
        "agent-c": {"sensor": 2.5, "network": 2.0, "compute": 1.0},
    }
    assignments: list[dict[str, object]] = []
    total_messages = 0
    for task_id in range(task_count):
        skill = rng.choice(["sensor", "network", "compute"])
        work_units = rng.randint(1, 5)
        announcement = {"task_id": task_id, "skill": skill, "work_units": work_units}
        bids = []
        for name, costs in agents.items():
            jitter = rng.random() * 0.05
            bids.append({"agent": name, "cost": round(work_units * costs[skill] + jitter, 3)})
        winner = min(bids, key=lambda item: (item["cost"], item["agent"]))
        total_messages += 1 + len(bids) + 1
        assignments.append(
            {
                "announcement": announcement,
                "bids": bids,
                "winner": winner,
            }
        )
    return {
        "seed": seed,
        "task_count": task_count,
        "message_count": total_messages,
        "assignments": assignments,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--tasks", type=int, default=8)
    args = parser.parse_args()
    print(json.dumps(allocate(args.seed, args.tasks), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
