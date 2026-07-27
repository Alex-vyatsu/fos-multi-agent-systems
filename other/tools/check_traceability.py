"""Проверка атомарной трассировки индикаторов и локальных ресурсов."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path


TARGET_FILES = (
    "README.md",
    "docs/rpd.md",
    "Midterm-1/README.md",
    "Midterm-1/kim-01-control-work.md",
    "Midterm-1/rubric-01.md",
    "Exam/kim-02-practical-task.md",
    "Exam/rubric-02.md",
)
FORBIDDEN_LEVEL_PATTERNS = (
    re.compile(r"O-2\.1[–-]O-2\.4\s*\(С\)"),
    re.compile(r"O-2\.1[–-]O-2\.4\s*\|\s*С"),
    re.compile(r"O-2\.1,\s*O-2\.3,\s*O-2\.4\s*\(уровень С\)"),
    re.compile(
        r"O-2\.1,\s*O-2\.2,\s*O-2\.3,\s*O-2\.4\s*"
        r"\(целевой уровень\s*[—-]\s*С\)"
    ),
    re.compile(r"O-2\.1[–-]O-2\.4[^.\n]*на среднем уровне"),
    re.compile(r"O-2\.3\s+на среднем уровне"),
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def local_path(root: Path, ref: str) -> Path:
    return root / ref.split("#", 1)[0]


def main(root_arg: str = ".") -> int:
    root = Path(root_arg).resolve()
    failures: list[str] = []

    catalog_rows = read_csv(root / "data/competency-catalog.csv")
    catalog = {
        row["indicator_code"]: {
            "wording": row["indicator_name"],
            "level": row["indicator_target_level"],
        }
        for row in catalog_rows
    }
    measurement_rows = read_csv(root / "data/indicator-evidence.csv")
    measurement = {row["indicator_id"]: row for row in measurement_rows}

    if len(measurement_rows) != len(measurement):
        failures.append("indicator-evidence.csv содержит повторяющиеся indicator_id")
    if set(measurement) != set(catalog):
        failures.append(
            "набор индикаторов атомарной матрицы не совпадает с competency-catalog.csv"
        )

    resources = read_csv(root / "data/resource-manifest.csv")
    resource_by_id = {row["resource_id"]: row for row in resources}
    if len(resources) != len(resource_by_id):
        failures.append("resource-manifest.csv содержит повторяющиеся resource_id")

    for resource_id, row in resource_by_id.items():
        path_or_url = row["path_or_url"]
        if path_or_url.startswith(("http://", "https://")):
            continue
        if not (root / path_or_url).is_file():
            failures.append(f"{resource_id}: локальный ресурс не найден: {path_or_url}")
        for kim_ref in filter(None, row["kim_refs"].split(";")):
            if not local_path(root, kim_ref).is_file():
                failures.append(f"{resource_id}: связанный КИМ не найден: {kim_ref}")
        for required in (
            "version_or_snapshot",
            "owner_role",
            "audience_access",
            "license_status",
            "last_access_check",
            "deprecation_status",
        ):
            if not row[required].strip():
                failures.append(f"{resource_id}: не заполнено поле {required}")

    human_view = (root / "docs/indicator-evidence.md").read_text(encoding="utf-8")
    for indicator_id, source in catalog.items():
        row = measurement.get(indicator_id)
        if row is None:
            continue
        if row["krm_wording_verbatim"] != source["wording"]:
            failures.append(f"{indicator_id}: формулировка не совпадает с КРМ")
        if row["level"] != source["level"]:
            failures.append(
                f"{indicator_id}: уровень {row['level']} не совпадает с КРМ "
                f"{source['level']}"
            )
        for field in ("kim_ref", "evidence_item_ref", "rubric_ref"):
            if not local_path(root, row[field]).is_file():
                failures.append(f"{indicator_id}: не найден {field}: {row[field]}")
        rubric_path = local_path(root, row["rubric_ref"])
        if rubric_path.is_file():
            rubric_text = rubric_path.read_text(encoding="utf-8")
            if row["rubric_row"] not in rubric_text:
                failures.append(
                    f"{indicator_id}: строка рубрики не найдена: {row['rubric_row']}"
                )
        for resource_id in filter(None, row["resource_refs"].split(";")):
            if resource_id not in resource_by_id:
                failures.append(f"{indicator_id}: неизвестный ресурс {resource_id}")
        if indicator_id not in human_view or source["wording"] not in human_view:
            failures.append(f"{indicator_id}: нет точной строки в docs/indicator-evidence.md")

    for relative in TARGET_FILES:
        path = root / relative
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_LEVEL_PATTERNS:
            if pattern.search(text):
                failures.append(
                    f"{relative}: запрещённая агрегация уровня: {pattern.pattern}"
                )

    ghost_entries = []
    for directory in root.glob("**/attachments"):
        entries = [item.name for item in directory.iterdir() if item.name != ".gitkeep"]
        ghost_entries.extend(f"{directory.relative_to(root)}/{name}" for name in entries)
    if ghost_entries:
        print("Непустые student-output placeholders:", ", ".join(ghost_entries))
    else:
        print("attachments: только явно обозначенные placeholders; ресурсами не считаются")

    print(f"Индикаторов в атомарной матрице: {len(measurement_rows)}")
    print(f"Локальных ресурсов в manifest: {len(resources)}")
    print(f"Ошибок трассировки: {len(failures)}")
    for failure in failures:
        print("   ", failure)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
