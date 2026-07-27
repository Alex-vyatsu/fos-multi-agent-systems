"""Проверка, что опубликованные предзащитные evidence воспроизводимы."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from examples.defense_experiment import run_experiment  # noqa: E402
from examples.exam_end_to_end import run as run_exam  # noqa: E402


def load_json(relative: str) -> dict[str, object]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def load_jsonl(relative: str) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in (ROOT / relative).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> int:
    failures: list[str] = []
    expected_run = run_exam(seed=42, pattern="reviewed_pipeline", task_count=8)
    actual_run = load_json("evidence/defense-run-seed42.json")
    if actual_run != expected_run:
        failures.append("defense-run-seed42.json не совпадает с повторным запуском")

    actual_trace = load_jsonl("evidence/defense-trace-seed42.jsonl")
    if actual_trace != expected_run["observability"]["trace"]:
        failures.append("defense-trace-seed42.jsonl не совпадает с trace запуска")
    required_boundaries = {"A2A", "MCP"}
    if not required_boundaries <= {event["boundary"] for event in actual_trace}:
        failures.append("trace не содержит обе границы A2A и MCP")
    if not any("tool_call_id" in event for event in actual_trace):
        failures.append("trace не связывает tool call")
    if not any("policy_decision_id" in event for event in actual_trace):
        failures.append("trace не связывает policy decision")
    if not any("artifact_id" in event for event in actual_trace):
        failures.append("trace не связывает artifact")
    serialized_trace = json.dumps(actual_trace, ensure_ascii=False).lower()
    if any(word in serialized_trace for word in ("password", "credential", "api_key")):
        failures.append("trace содержит запрещённое чувствительное поле")

    expected_experiment = run_experiment()
    actual_experiment = load_json("evidence/pattern-experiment.json")
    if actual_experiment != expected_experiment:
        failures.append("pattern-experiment.json не совпадает с повторным экспериментом")

    if not actual_experiment.get("passed"):
        failures.append("hard gates эксперимента не пройдены")
    if actual_run.get("approval_state") != "awaiting_human_decision":
        failures.append("ответственное решение не оставлено человеку")

    print(f"Evidence-файлов проверено: 3")
    print(f"Ошибок evidence: {len(failures)}")
    for failure in failures:
        print("   ", failure)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
