"""Сравнение IQL и упрощённого VDN-style CTDE на общей игре."""

from __future__ import annotations

import argparse
import itertools
import json
import random
from statistics import mean

try:
    from examples.m5_independent_q import train as train_iql
except ModuleNotFoundError:  # direct: python examples/m5_ctde_comparison.py
    from m5_independent_q import train as train_iql


SEEDS = (7, 42, 99)


def train_vdn(seed: int = 42, episodes: int = 2_000) -> dict[str, object]:
    """Одношаговый VDN-style baseline с централизованным sum-mixer."""

    rng = random.Random(seed)
    utilities = [[0.0, 0.0], [0.0, 0.0]]
    alpha = 0.08
    rewards: list[int] = []
    joint_actions = list(itertools.product(range(2), repeat=2))

    for episode in range(episodes):
        epsilon = max(0.02, 0.35 * (1 - episode / episodes))
        if rng.random() < epsilon:
            actions = joint_actions[rng.randrange(len(joint_actions))]
        else:
            actions = max(
                joint_actions,
                key=lambda pair: (
                    utilities[0][pair[0]] + utilities[1][pair[1]],
                    tuple(-action for action in pair),
                ),
            )
        reward = 1 if actions[0] == actions[1] else 0
        rewards.append(reward)
        joint_value = utilities[0][actions[0]] + utilities[1][actions[1]]
        td_error = reward - joint_value
        for agent, action in enumerate(actions):
            utilities[agent][action] += alpha * td_error / 2

    learned_actions = [
        max(range(2), key=agent_utilities.__getitem__)
        for agent_utilities in utilities
    ]
    return {
        "algorithm": "VDN-style tabular CTDE",
        "seed": seed,
        "episodes": episodes,
        "last_200_coordination_rate": round(sum(rewards[-200:]) / 200, 3),
        "learned_actions": learned_actions,
        "local_utilities": [
            [round(value, 4) for value in agent_utilities]
            for agent_utilities in utilities
        ],
        "training_boundary": (
            "centralized sum-mixer during training; local argmax execution"
        ),
    }


def compare_algorithms() -> dict[str, object]:
    runs: list[dict[str, object]] = []
    for seed in SEEDS:
        iql = train_iql(seed=seed, episodes=2_000)
        vdn = train_vdn(seed=seed, episodes=2_000)
        runs.extend(
            [
                {
                    "algorithm": "IQL",
                    "seed": seed,
                    "coordination_rate": iql["last_200_coordination_rate"],
                    "learned_actions": iql["learned_actions"],
                },
                {
                    "algorithm": "VDN-style CTDE",
                    "seed": seed,
                    "coordination_rate": vdn["last_200_coordination_rate"],
                    "learned_actions": vdn["learned_actions"],
                },
            ]
        )
    summary = {}
    for algorithm in ("IQL", "VDN-style CTDE"):
        values = [
            float(run["coordination_rate"])
            for run in runs
            if run["algorithm"] == algorithm
        ]
        summary[algorithm] = {
            "mean_coordination_rate": round(mean(values), 3),
            "range": [min(values), max(values)],
            "all_runs_coordinated": all(value >= 0.9 for value in values),
        }
    return {
        "environment": "one-state cooperative two-agent coordination game",
        "seeds": list(SEEDS),
        "episodes": 2_000,
        "runs": runs,
        "summary": summary,
        "passed": all(item["all_runs_coordinated"] for item in summary.values()),
        "claim_boundary": (
            "учебный tabular VDN-style baseline, не реализация промышленного "
            "QMIX/MADDPG и не доказательство переноса на другие среды"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    result = train_vdn(args.seed) if args.seed is not None else compare_algorithms()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
