"""Единая локальная проверка репозитория."""

from __future__ import annotations

import subprocess
import sys


COMMANDS = [
    [sys.executable, "other/tools/check_links.py"],
    [sys.executable, "other/tools/check_weights.py"],
    [sys.executable, "other/tools/check_traceability.py"],
    [sys.executable, "other/tools/check_structure.py"],
    [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
]


def main() -> int:
    for command in COMMANDS:
        print(f"\n$ {' '.join(command)}", flush=True)
        result = subprocess.run(command, check=False)
        if result.returncode:
            print(f"Проверка завершилась с кодом {result.returncode}")
            return result.returncode
    print("\nВсе локальные проверки пройдены.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
