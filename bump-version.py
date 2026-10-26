#!/usr/bin/env python3
"""Повышение версии AI_NLC на +1.

Схема (как попросил владелец): 0.0.1 -> 0.0.2 -> ... -> 0.0.9 -> 0.1.0 -> 0.1.1 ...
Т.е. +1 к последней цифре; если она стала больше 9 — сброс в 0 и +1 к предыдущей
(0.9.9 -> 1.0.0). Использование:

    python3 bump-version.py "что изменилось"   # поднять версию и записать в CHANGELOG.md
    python3 bump-version.py --dry-run          # только показать следующую версию

Источники правды синхронно обновляются: файл VERSION и APP_VERSION в index.html.
"""
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
VERSION_FILE = ROOT / "VERSION"
INDEX_FILE = ROOT / "index.html"
CHANGELOG_FILE = ROOT / "CHANGELOG.md"


def bump(version: str) -> str:
    parts = version.strip().split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        raise ValueError(f"Невалидная версия: {version!r} (ожидается X.Y.Z)")
    major, minor, patch = map(int, parts)
    patch += 1
    if patch > 9:
        patch, minor = 0, minor + 1
    if minor > 9:
        minor, major = 0, major + 1
    return f"{major}.{minor}.{patch}"


def main() -> None:
    args = [a for a in sys.argv[1:]]
    dry = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]
    note = args[0] if args else "обновление"

    current = VERSION_FILE.read_text(encoding="utf-8").strip()
    new = bump(current)
    print(f"{current} -> {new}")
    if dry:
        return

    VERSION_FILE.write_text(new + "\n", encoding="utf-8")

    html = INDEX_FILE.read_text(encoding="utf-8")
    html_new, n = re.subn(r"const APP_VERSION = '[^']+'", f"const APP_VERSION = '{new}'", html)
    if n != 1:
        raise SystemExit("Не нашёл APP_VERSION в index.html — версия в интерфейсе не обновлена!")
    INDEX_FILE.write_text(html_new, encoding="utf-8")

    entry = f"## v{new} — {date.today().isoformat()}\n- {note}\n\n"
    old = CHANGELOG_FILE.read_text(encoding="utf-8") if CHANGELOG_FILE.exists() else "# История версий AI_NLC\n\n"
    head, _, rest = old.partition("\n\n")
    CHANGELOG_FILE.write_text(f"{head}\n\n{entry}{rest}", encoding="utf-8")
    print(f"Обновлены: VERSION, index.html (APP_VERSION), CHANGELOG.md")


if __name__ == "__main__":
    main()
