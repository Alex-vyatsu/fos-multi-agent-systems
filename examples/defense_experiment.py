"""Воспроизводимый предзащитный эксперимент по двум LLM-паттернам."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean

try:
    from examples.exam_end_to_end import run as run_exam
    from examples.exam_end_to_end import write_json
    from examples.m5_ctde_comparison import compare_algorithms
except ModuleNotFoundError:  # direct: python examples/defense_experiment.py
    from exam_end_to_end import run as run_exam
    from exam_end_to_end import write_json
    from m5_ctde_comparison import compare_algorithms


SEEDS = (7, 42, 99)
PATTERNS = ("orchestrator", "reviewed_pipeline")
SCALE_TASK_COUNTS = (4, 8, 12)


def _record(result: dict[str, object]) -> dict[str, object]:
    allocation = result["allocation"]
    observability = result["observability"]
    metrics = observability["metrics"]
    return {
        "seed": result["seed"],
        "pattern": result["pattern"],
        "task_count": allocation["task_count"],
        "message_count": allocation["message_count"],
        "total_winning_cost": allocation["total_winning_cost"],
        "trace_event_count": metrics["event_count"],
        "latency_budget_ms": metrics["latency_budget_ms"],
        "external_cost_usd": metrics["external_cost_usd"],
        "acceptance_passed": sum(result["acceptance"].values()),
        "acceptance_total": len(result["acceptance"]),
        "passed": result["passed"],
    }


def _summarize(records: list[dict[str, object]]) -> dict[str, object]:
    return {
        "runs": len(records),
        "pass_rate": round(mean(int(record["passed"]) for record in records), 3),
        "mean_total_winning_cost": round(
            mean(float(record["total_winning_cost"]) for record in records),
            3,
        ),
        "winning_cost_range": [
            min(float(record["total_winning_cost"]) for record in records),
            max(float(record["total_winning_cost"]) for record in records),
        ],
        "mean_trace_event_count": round(
            mean(int(record["trace_event_count"]) for record in records),
            3,
        ),
        "mean_latency_budget_ms": round(
            mean(int(record["latency_budget_ms"]) for record in records),
            3,
        ),
        "external_cost_usd": round(
            sum(float(record["external_cost_usd"]) for record in records),
            4,
        ),
    }


def run_experiment() -> dict[str, object]:
    marl_comparison = compare_algorithms()
    comparison_runs = [
        _record(run_exam(seed=seed, pattern=pattern, task_count=8))
        for pattern in PATTERNS
        for seed in SEEDS
    ]
    by_pattern = {
        pattern: _summarize(
            [record for record in comparison_runs if record["pattern"] == pattern]
        )
        for pattern in PATTERNS
    }

    scale_runs = [
        _record(
            run_exam(
                seed=42,
                pattern="reviewed_pipeline",
                task_count=task_count,
            )
        )
        for task_count in SCALE_TASK_COUNTS
    ]
    failure = run_exam(
        seed=42,
        pattern="reviewed_pipeline",
        task_count=8,
        inject_tool_failure=True,
    )
    hard_gates = {
        "all_comparison_runs_pass": all(
            record["passed"] for record in comparison_runs
        ),
        "all_scale_runs_pass": all(record["passed"] for record in scale_runs),
        "failure_detected": failure["protocol_state"] == "failed",
        "recovery_completed": failure["recovery_state"] == "completed",
        "no_external_api_cost": all(
            float(record["external_cost_usd"]) == 0.0
            for record in comparison_runs
        ),
        "marl_iql_vdn_comparison_passed": marl_comparison["passed"],
    }
    return {
        "experiment_id": "defense-patterns-seeds-scale-recovery-v1",
        "configurations": {
            "seeds": list(SEEDS),
            "patterns": list(PATTERNS),
            "scale_task_counts": list(SCALE_TASK_COUNTS),
            "profile": "minimal CPU-only deterministic protocol slice",
        },
        "comparison_runs": comparison_runs,
        "pattern_summary": by_pattern,
        "marl_comparison": marl_comparison,
        "scale_runs": scale_runs,
        "local_change": {
            "change": "tool_available: true → false → recovery true",
            "protocol_state": failure["protocol_state"],
            "recovery_state": failure["recovery_state"],
            "trace_event_count": failure["observability"]["metrics"]["event_count"],
        },
        "decision": {
            "low_risk": "orchestrator",
            "high_risk": "reviewed_pipeline",
            "reason": (
                "reviewed_pipeline сохраняет те же hard gates и добавляет "
                "независимую проверку ценой дополнительных событий и latency budget"
            ),
        },
        "hard_gates": hard_gates,
        "passed": all(hard_gates.values()),
        "claim_boundary": (
            "результат относится к детерминированному semantic contract slice; "
            "качество реальной LLM и wire-conformance не проверялись"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_experiment()
    if args.output is not None:
        write_json(args.output, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
