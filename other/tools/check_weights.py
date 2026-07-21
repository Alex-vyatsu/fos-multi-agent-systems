"""Проверка согласованности весов критериев в рубриках ФОС.

Запуск из корня репозитория:

    python other/tools/check_weights.py

Для каждого файла rubric-*.md суммируются веса критериев (строки таблицы,
начинающиеся с «| **К») и сравниваются с заявленным максимумом
(«**Максимум:** N баллов»).

Код возврата: 0 — все рубрики согласованы, 1 — есть расхождения.
"""

import os
import re
import sys

RUBRIC_RE = re.compile(r"rubric-\d+\.md$")
MAX_RE = re.compile(r"\*\*Максимум:\*\*\s*([\d.]+)")
NUMBER_RE = re.compile(r"\d+(\.\d+)?")


def criterion_weights(text: str):
    weights = []
    for line in text.splitlines():
        if not line.startswith("| **К"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        for cell in cells[1:]:
            if NUMBER_RE.fullmatch(cell):
                weights.append(float(cell))
                break
    return weights


def main(root: str) -> int:
    failures = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for name in sorted(filenames):
            if not RUBRIC_RE.match(name):
                continue
            path = os.path.join(dirpath, name)
            text = open(path, encoding="utf-8").read()
            match = MAX_RE.search(text)
            declared = float(match.group(1)) if match else None
            weights = criterion_weights(text)
            total = round(sum(weights), 3)
            ok = declared is not None and abs(total - declared) < 1e-6
            failures += 0 if ok else 1
            status = "OK " if ok else "!!!"
            rel = os.path.relpath(path, root)
            print(f"{status} {rel:<40} критериев={len(weights)}  сумма={total}  заявлено={declared}")
    print("Расхождений:", failures)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
