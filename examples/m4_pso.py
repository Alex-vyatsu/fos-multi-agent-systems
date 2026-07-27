"""Упрощённый PSO для функции sphere и сопоставимый случайный поиск."""

from __future__ import annotations

import argparse
import json
import random


def sphere(point: list[float]) -> float:
    return sum(value * value for value in point)


def run(seed: int = 42, particles: int = 12, steps: int = 30) -> dict[str, object]:
    rng = random.Random(seed)
    positions = [[rng.uniform(-5, 5), rng.uniform(-5, 5)] for _ in range(particles)]
    velocities = [[0.0, 0.0] for _ in range(particles)]
    personal = [point[:] for point in positions]
    personal_scores = [sphere(point) for point in personal]
    initial_best = min(personal_scores)

    for _ in range(steps):
        global_index = min(range(particles), key=personal_scores.__getitem__)
        global_best = personal[global_index][:]
        for index in range(particles):
            for coordinate in range(2):
                inertia = 0.65 * velocities[index][coordinate]
                cognitive = 1.4 * rng.random() * (
                    personal[index][coordinate] - positions[index][coordinate]
                )
                social = 1.4 * rng.random() * (
                    global_best[coordinate] - positions[index][coordinate]
                )
                velocities[index][coordinate] = inertia + cognitive + social
                positions[index][coordinate] += velocities[index][coordinate]
            score = sphere(positions[index])
            if score < personal_scores[index]:
                personal[index] = positions[index][:]
                personal_scores[index] = score

    random_best = min(
        sphere([rng.uniform(-5, 5), rng.uniform(-5, 5)])
        for _ in range(particles * steps)
    )
    return {
        "seed": seed,
        "particles": particles,
        "steps": steps,
        "initial_best": round(initial_best, 6),
        "pso_best": round(min(personal_scores), 6),
        "random_search_best": round(random_best, 6),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--particles", type=int, default=12)
    parser.add_argument("--steps", type=int, default=30)
    args = parser.parse_args()
    print(json.dumps(run(args.seed, args.particles, args.steps), indent=2))


if __name__ == "__main__":
    main()
