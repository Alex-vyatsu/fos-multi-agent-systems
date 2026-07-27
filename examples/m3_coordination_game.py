"""Минимальный пример матричной и повторяющейся игры для модуля 3."""

from __future__ import annotations

import argparse
import json
import random
from collections.abc import Callable, Sequence


Payoff = tuple[int, int]
PayoffMatrix = Sequence[Sequence[Payoff]]
Strategy = Callable[[list[str], list[str]], str]


COORDINATION_GAME: tuple[tuple[Payoff, ...], ...] = (
    ((4, 4), (0, 1)),
    ((1, 0), (3, 3)),
)
PRISONERS_DILEMMA: dict[tuple[str, str], Payoff] = {
    ("C", "C"): (3, 3),
    ("C", "D"): (0, 5),
    ("D", "C"): (5, 0),
    ("D", "D"): (1, 1),
}


def pure_nash_equilibria(matrix: PayoffMatrix) -> list[tuple[int, int]]:
    """Найти равновесия Нэша в чистых стратегиях биматричной игры."""

    if not matrix or not matrix[0]:
        raise ValueError("матрица выигрышей не должна быть пустой")
    column_count = len(matrix[0])
    if any(len(row) != column_count for row in matrix):
        raise ValueError("матрица выигрышей должна быть прямоугольной")

    equilibria: list[tuple[int, int]] = []
    for row_index, row in enumerate(matrix):
        for column_index, payoff in enumerate(row):
            row_best = max(candidate[column_index][0] for candidate in matrix)
            column_best = max(candidate[1] for candidate in row)
            if payoff[0] == row_best and payoff[1] == column_best:
                equilibria.append((row_index, column_index))
    return equilibria


def pareto_optimal_outcomes(matrix: PayoffMatrix) -> list[tuple[int, int]]:
    """Вернуть исходы, которые не доминируются другим исходом по Парето."""

    outcomes = [
        (row_index, column_index, payoff)
        for row_index, row in enumerate(matrix)
        for column_index, payoff in enumerate(row)
    ]
    optimal: list[tuple[int, int]] = []
    for row_index, column_index, payoff in outcomes:
        dominated = any(
            other[0] >= payoff[0]
            and other[1] >= payoff[1]
            and other != payoff
            for _, _, other in outcomes
        )
        if not dominated:
            optimal.append((row_index, column_index))
    return optimal


def always_cooperate(_: list[str], __: list[str]) -> str:
    return "C"


def always_defect(_: list[str], __: list[str]) -> str:
    return "D"


def tit_for_tat(_: list[str], opponent_history: list[str]) -> str:
    return opponent_history[-1] if opponent_history else "C"


STRATEGIES: dict[str, Strategy] = {
    "all_c": always_cooperate,
    "all_d": always_defect,
    "tit_for_tat": tit_for_tat,
}


def play_repeated(
    first: Strategy,
    second: Strategy,
    *,
    rounds: int,
    noise: float,
    rng: random.Random,
) -> dict[str, object]:
    """Сыграть повторяющуюся дилемму заключённого с ошибками исполнения."""

    if rounds <= 0:
        raise ValueError("число раундов должно быть положительным")
    if not 0.0 <= noise <= 1.0:
        raise ValueError("noise должен находиться в диапазоне [0, 1]")

    first_history: list[str] = []
    second_history: list[str] = []
    first_total = 0
    second_total = 0
    cooperation_actions = 0

    for _ in range(rounds):
        first_action = first(first_history, second_history)
        second_action = second(second_history, first_history)
        if rng.random() < noise:
            first_action = "D" if first_action == "C" else "C"
        if rng.random() < noise:
            second_action = "D" if second_action == "C" else "C"
        payoff = PRISONERS_DILEMMA[(first_action, second_action)]
        first_total += payoff[0]
        second_total += payoff[1]
        cooperation_actions += int(first_action == "C") + int(second_action == "C")
        first_history.append(first_action)
        second_history.append(second_action)

    return {
        "first_average_payoff": round(first_total / rounds, 3),
        "second_average_payoff": round(second_total / rounds, 3),
        "cooperation_rate": round(cooperation_actions / (2 * rounds), 3),
    }


def run(seed: int = 42, rounds: int = 100, noise: float = 0.05) -> dict[str, object]:
    rng = random.Random(seed)
    tournament: dict[str, dict[str, object]] = {}
    for first_name, second_name in (
        ("all_c", "all_d"),
        ("tit_for_tat", "tit_for_tat"),
        ("tit_for_tat", "all_d"),
    ):
        tournament[f"{first_name}_vs_{second_name}"] = play_repeated(
            STRATEGIES[first_name],
            STRATEGIES[second_name],
            rounds=rounds,
            noise=noise,
            rng=rng,
        )
    return {
        "seed": seed,
        "rounds": rounds,
        "noise": noise,
        "pure_nash_equilibria": pure_nash_equilibria(COORDINATION_GAME),
        "pareto_optimal_outcomes": pareto_optimal_outcomes(COORDINATION_GAME),
        "tournament": tournament,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--rounds", type=int, default=100)
    parser.add_argument("--noise", type=float, default=0.05)
    args = parser.parse_args()
    print(json.dumps(run(args.seed, args.rounds, args.noise), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
