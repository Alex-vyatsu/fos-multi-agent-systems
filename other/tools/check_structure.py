"""Проверка состава ФОС и минимального воспроизводимого контура."""

from __future__ import annotations

import sys
from pathlib import Path


EXPECTED_KIM = 23
EXPECTED_RUBRICS = 17
REQUIRED_FILES = [
    "requirements.txt",
    "pyproject.toml",
    "Dockerfile",
    "LICENSE-CODE.md",
    "examples/README.md",
    "examples/m1_reactive_agents.py",
    "examples/m2_contract_net.py",
    "examples/m3_coordination_game.py",
    "examples/m4_pso.py",
    "examples/m5_independent_q.py",
    "examples/m6_guarded_orchestrator.py",
    "examples/m6_protocol_slice.py",
    "examples/exam_end_to_end.py",
    "data/indicator-evidence.csv",
    "data/resource-manifest.csv",
    "docs/indicator-evidence.md",
    "docs/resource-profiles.md",
    "docs/clean-run-2026-07-27.md",
    "docs/evaluation-2026-07-27.md",
    "resources/datasets/generate_requests.py",
    "resources/datasets/generated/requests_seed42.csv",
    "templates/student-repository/README.md",
    "templates/student-repository/architecture-decision.md",
    "templates/student-repository/experiment-log.csv",
    "templates/student-repository/report.md",
    "templates/student-repository/ai-use-disclosure.md",
    "team/ownership.md",
]
INDICATORS = [
    "O-2.1",
    "O-2.2",
    "O-2.3",
    "O-2.4",
    "ML-6.1",
    "ML-6.3",
    "LLM-4.1",
    "LLM-4.3",
    "FC-3.3",
]


def main(root_arg: str = ".") -> int:
    root = Path(root_arg).resolve()
    failures: list[str] = []
    kim = sorted(root.glob("**/kim-*.md"))
    rubrics = sorted(root.glob("**/rubric-*.md"))

    if len(kim) != EXPECTED_KIM:
        failures.append(f"ожидалось КИМ: {EXPECTED_KIM}, найдено: {len(kim)}")
    if len(rubrics) != EXPECTED_RUBRICS:
        failures.append(f"ожидалось рубрик: {EXPECTED_RUBRICS}, найдено: {len(rubrics)}")

    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            failures.append(f"нет обязательного файла: {relative}")

    readme = (root / "README.md").read_text(encoding="utf-8")
    for indicator in INDICATORS:
        if indicator not in readme:
            failures.append(f"индикатор не отражён в README: {indicator}")

    print(f"КИМ: {len(kim)}")
    print(f"Рубрик: {len(rubrics)}")
    print(f"Обязательных файлов: {len(REQUIRED_FILES)}")
    print(f"Ошибок структуры: {len(failures)}")
    for failure in failures:
        print("   ", failure)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
