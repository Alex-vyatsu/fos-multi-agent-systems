"""Сквозной smoke-сценарий экзамена: данные → координация → tool boundary."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

try:
    from examples.m2_contract_net import allocate
    from examples.m6_protocol_slice import PATTERNS, run_demo, trace_metrics
except ModuleNotFoundError:  # direct: python examples/exam_end_to_end.py
    from m2_contract_net import allocate
    from m6_protocol_slice import PATTERNS, run_demo, trace_metrics


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
    pattern: str = "reviewed_pipeline",
    task_count: int = 8,
) -> dict[str, object]:
    requests = load_requests(dataset)
    if task_count < 1:
        raise ValueError("число задач должно быть положительным")
    allocation = allocate(seed=seed, task_count=min(task_count, len(requests)))
    protocol = run_demo(
        tool_available=not inject_tool_failure,
        pattern=pattern,
        interaction_id=f"exam-{seed}-attempt-1",
    )

    recovered = False
    recovery_protocol = None
    if protocol["task_state"] == "failed":
        recovery_protocol = run_demo(
            tool_available=True,
            pattern=pattern,
            interaction_id=f"exam-{seed}-attempt-2",
        )
        recovered = recovery_protocol["task_state"] == "completed"

    task_ids = [
        item["announcement"]["task_id"]
        for item in allocation["assignments"]
    ]
    total_winning_cost = round(
        sum(float(item["winner"]["cost"]) for item in allocation["assignments"]),
        3,
    )
    trace = list(protocol["trace"])
    if recovery_protocol is not None:
        trace.extend(recovery_protocol["trace"])
    effective_protocol = (
        recovery_protocol if recovery_protocol is not None else protocol
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
    trace_complete = bool(trace) and all(
        required_trace_fields <= event.keys() for event in trace
    )
    boundaries = {event["boundary"] for event in trace}
    acceptance = {
        "functional": task_ids == list(range(len(task_ids))),
        "reproducible": allocation == allocate(seed=seed, task_count=len(task_ids)),
        "observable": trace_complete and {"A2A", "MCP"} <= boundaries,
        "fault_safe": protocol["task_state"] != "failed" or recovered,
        "responsible": (
            effective_protocol["approval_state"] == "awaiting_human_decision"
            and effective_protocol["claim_boundary"].startswith(
                "semantic contract slice"
            )
        ),
    }
    return {
        "seed": seed,
        "pattern": pattern,
        "dataset_rows": len(requests),
        "allocation": {
            "task_count": allocation["task_count"],
            "message_count": allocation["message_count"],
            "total_winning_cost": total_winning_cost,
            "mean_winning_cost": round(total_winning_cost / len(task_ids), 3),
        },
        "protocol_state": protocol["task_state"],
        "review_state": effective_protocol["review_state"],
        "recovery_state": (
            recovery_protocol["task_state"] if recovery_protocol is not None else "not_needed"
        ),
        "observability": {
            "trace": trace,
            "metrics": trace_metrics(trace),
            "versions": effective_protocol["versions"],
            "metric_boundary": (
                "latency_ms — детерминированный учебный budget; "
                "реальное время фиксируется clean run"
            ),
        },
        "approval_state": effective_protocol["approval_state"],
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
    }


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_trace(path: Path, trace: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(
            json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n"
            for event in trace
        ),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("resources/datasets/generated/requests_seed42.csv"),
    )
    parser.add_argument("--inject-tool-failure", action="store_true")
    parser.add_argument("--pattern", choices=sorted(PATTERNS), default="reviewed_pipeline")
    parser.add_argument("--tasks", type=int, default=8)
    parser.add_argument("--summary-output", type=Path)
    parser.add_argument("--trace-output", type=Path)
    args = parser.parse_args()
    result = run(
        seed=args.seed,
        dataset=args.dataset,
        inject_tool_failure=args.inject_tool_failure,
        pattern=args.pattern,
        task_count=args.tasks,
    )
    if args.summary_output is not None:
        write_json(args.summary_output, result)
    if args.trace_output is not None:
        write_trace(args.trace_output, result["observability"]["trace"])
    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
