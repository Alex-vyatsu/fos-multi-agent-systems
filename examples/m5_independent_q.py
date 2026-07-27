"""Независимое Q-обучение двух агентов в кооперативной игре."""

from __future__ import annotations

import argparse
import json
import random


def train(seed: int = 42, episodes: int = 2_000) -> dict[str, object]:
    rng = random.Random(seed)
    q_values = [[0.0, 0.0], [0.0, 0.0]]
    alpha = 0.08
    rewards: list[int] = []

    for episode in range(episodes):
        epsilon = max(0.02, 0.35 * (1 - episode / episodes))
        actions = []
        for agent in range(2):
            if rng.random() < epsilon:
                actions.append(rng.randrange(2))
            else:
                actions.append(max(range(2), key=q_values[agent].__getitem__))
        reward = 1 if actions[0] == actions[1] else 0
        rewards.append(reward)
        for agent, action in enumerate(actions):
            q_values[agent][action] += alpha * (reward - q_values[agent][action])

    evaluation_actions = [max(range(2), key=values.__getitem__) for values in q_values]
    return {
        "seed": seed,
        "episodes": episodes,
        "last_200_coordination_rate": round(sum(rewards[-200:]) / 200, 3),
        "learned_actions": evaluation_actions,
        "q_values": [[round(value, 4) for value in values] for values in q_values],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--episodes", type=int, default=2_000)
    args = parser.parse_args()
    print(json.dumps(train(args.seed, args.episodes), indent=2))


if __name__ == "__main__":
    main()
