"""Генератор воспроизводимого потока заявок для КИМ-2.1."""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path


FIELDS = [
    "request_id",
    "release_tick",
    "priority",
    "work_units",
    "required_skill",
]


def generate(seed: int = 42, count: int = 20) -> list[dict[str, object]]:
    rng = random.Random(seed)
    rows = []
    tick = 0
    for request_id in range(1, count + 1):
        tick += rng.randint(0, 2)
        rows.append(
            {
                "request_id": f"R{request_id:03d}",
                "release_tick": tick,
                "priority": rng.randint(1, 3),
                "work_units": rng.randint(1, 8),
                "required_skill": rng.choice(["sensor", "network", "compute"]),
            }
        )
    return rows


def write_csv(rows: list[dict[str, object]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("resources/datasets/generated/requests_seed42.csv"),
    )
    args = parser.parse_args()
    write_csv(generate(args.seed, args.count), args.output)
    print(f"Создано заявок: {args.count}; файл: {args.output}")


if __name__ == "__main__":
    main()
