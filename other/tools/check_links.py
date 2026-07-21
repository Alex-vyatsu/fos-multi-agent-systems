"""Проверка внутренних markdown-ссылок и якорей репозитория ФОС.

Запуск из корня репозитория:

    python other/tools/check_links.py

Проверяются только относительные ссылки: существование файла и наличие
заголовка, соответствующего якорю. Внешние ссылки (http/mailto) не
проверяются — их доступность подтверждает ответственный преподаватель
перед началом семестра (см. resources/README.md).

Код возврата: 0 — ошибок нет, 1 — найдены битые ссылки или якоря.
"""

import os
import re
import sys
import urllib.parse

LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$", re.M)


def slug(title: str) -> str:
    """Приближение к правилам построения якорей GitHub."""
    s = title.strip().lower()
    s = re.sub(r"[`*_\[\]()]", "", s)
    s = re.sub(r"[^\w\s\-–—]", "", s, flags=re.UNICODE)
    s = s.replace("–", "").replace("—", "")
    return re.sub(r"\s+", "-", s.strip())


def md_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for name in filenames:
            if name.endswith(".md"):
                yield os.path.join(dirpath, name)


def main(root: str) -> int:
    anchors = {}
    for path in md_files(root):
        text = open(path, encoding="utf-8").read()
        anchors[os.path.normpath(path)] = {slug(m.group(1)) for m in HEADING_RE.finditer(text)}

    broken_links, broken_anchors = [], []
    for path in md_files(root):
        text = open(path, encoding="utf-8").read()
        for match in LINK_RE.finditer(text):
            link = match.group(1)
            if link.startswith(("http", "mailto")):
                continue
            file_part, _, anchor = link.partition("#")
            file_part = urllib.parse.unquote(file_part)
            anchor = urllib.parse.unquote(anchor)
            target = os.path.normpath(
                path if not file_part else os.path.join(os.path.dirname(path), file_part)
            )
            rel = os.path.relpath(path, root)
            if not os.path.exists(target):
                broken_links.append(f"{rel} -> {link}")
            elif anchor and target.endswith(".md") and anchor not in anchors.get(target, set()):
                broken_anchors.append(f"{rel} -> {link}")

    print(f"Битых ссылок: {len(broken_links)}")
    for item in broken_links:
        print("   ", item)
    print(f"Битых якорей: {len(broken_anchors)}")
    for item in broken_anchors:
        print("   ", item)
    return 1 if broken_links or broken_anchors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
