"""Сквозной smoke-сценарий экзамена: данные → координация → tool boundary."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

try:
    from examples.m2_contract_net import allocate
    from examples.m6_protocol_slice import run_demo
except ModuleNotFoundError:  # direct: python examples/exam_end_to_end.py
    from m2_contract_net import allocate
    from m6_protocol_slice import run_demo


class ResourceUnavailable(RuntimeError):
    """Входной ресурс отсутствует и должен быть восстановлен явным шагом."""


def load_requests(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise ResourceUnavailable(
            f"нет набора данных {path}; выполните "
            "python resources/datasets/generate_requests.py --seed 42 --count 12 "
            "--output resources/datasets/generated/requests_seed42.csv"
        )
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def run(
    *,
    seed: int = 42,
    dataset: Path = Path("resources/datasets/generated/requests_seed42.csv"),
    inject_tool_failure: bool = False,
) -> dict[str, object]:
    requests = load_requests(dataset)
    allocation = allocate(seed=seed, task_count=min(8, len(requests)))
    protocol = run_demo(tool_available=not inject_tool_failure)

    recovered = False
    recovery_protocol = None
    if protocol["task_state"] == "failed":
        recovery_protocol = run_demo(tool_available=True)
        recovered = recovery_protocol["task_state"] == "completed"

    task_ids = [
        item["announcement"]["task_id"]
        for item in allocation["assignments"]
    ]
    acceptance = {
        "functional": task_ids == list(range(len(task_ids))),
        "reproducible": allocation == allocate(seed=seed, task_count=len(task_ids)),
        "observable": bool(protocol["trace"]),
        "fault_safe": protocol["task_state"] != "failed" or recovered,
        "responsible": protocol["claim_boundary"].startswith("semantic contract slice"),
    }
    return {
        "seed": seed,
        "dataset_rows": len(requests),
        "allocation": {
            "task_count": allocation["task_count"],
            "message_count": allocation["message_count"],
        },
        "protocol_state": protocol["task_state"],
        "recovery_state": (
            recovery_protocol["task_state"] if recovery_protocol is not None else "not_needed"
        ),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("resources/datasets/generated/requests_seed42.csv"),
    )
    parser.add_argument("--inject-tool-failure", action="store_true")
    args = parser.parse_args()
    print(
        json.dumps(
            run(
                seed=args.seed,
                dataset=args.dataset,
                inject_tool_failure=args.inject_tool_failure,
            ),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
