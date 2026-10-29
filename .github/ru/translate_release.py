"""Накладывает русификацию из ветки russian на тег релиза оригинального проекта.

Использование:
    python translate_release.py <тег> <ветка-перевода> <ветка-оригинала>

1. Все изменения ветки перевода относительно оригинала (кроме .github/)
   собираются в один коммит.
2. Этот коммит переносится на тег через cherry-pick. В местах, где оригинал
   успел поменять тот же код, побеждает код оригинала (-X ours), чтобы сборка
   не сломалась.
3. В строках, которые оригинал не менял, перевод восстанавливается по словарю
   «английская строка -> русская строка», собранному из ветки перевода.
4. Отчёт пишется в ru-report.md (идёт в описание релиза).
"""

import difflib
import os
import re
import subprocess
import sys
import tempfile

CYRILLIC = re.compile("[А-Яа-яЁё]")


def git(*args: str, env: dict | None = None, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args], capture_output=True, text=True, env=env, encoding="utf-8"
    )
    if check and result.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed:\n{result.stderr}")
    return result.stdout


def squash_translation(base: str, russian: str) -> str:
    """Один коммит поверх base с деревом ветки перевода, но с .github из base.

    .github не переносится: токен GitHub Actions не может менять workflow-файлы,
    а сборке релиза нужны workflow оригинала.
    """
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "GIT_INDEX_FILE": os.path.join(tmp, "index")}
        git("read-tree", russian, env=env)
        git("rm", "-r", "-q", "--cached", "--ignore-unmatch", ".github", env=env)
        git("read-tree", "--prefix=.github/", f"{base}:.github", env=env)
        tree = git("write-tree", env=env).strip()
    return git(
        "commit-tree", tree, "-p", base, "-m", "Русская локализация"
    ).strip()


def translation_map(base: str, squash: str) -> dict[str, dict[str, str]]:
    """{файл: {английская строка: русская строка}} по построчному diff."""
    result: dict[str, dict[str, str]] = {}
    files = git("diff", "--name-only", "--diff-filter=M", base, squash).split("\n")
    for path in filter(None, files):
        old = git("show", f"{base}:{path}", check=False).splitlines()
        new = git("show", f"{squash}:{path}", check=False).splitlines()
        pairs: dict[str, str] = {}
        ambiguous: set[str] = set()
        matcher = difflib.SequenceMatcher(None, old, new, autojunk=False)
        for op, i1, i2, j1, j2 in matcher.get_opcodes():
            if op != "replace" or i2 - i1 != j2 - j1:
                continue
            for a, b in zip(old[i1:i2], new[j1:j2]):
                a, b = a.strip(), b.strip()
                if not a or CYRILLIC.search(a) or not CYRILLIC.search(b):
                    continue
                if pairs.get(a, b) != b:
                    ambiguous.add(a)
                pairs[a] = b
        for a in ambiguous:
            del pairs[a]
        if pairs:
            result[path] = pairs
    return result


def restore_lines(mapping: dict[str, dict[str, str]]) -> dict[str, int]:
    """Переводит строки, оставшиеся английскими после cherry-pick."""
    restored: dict[str, int] = {}
    for path, pairs in mapping.items():
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8", newline="") as f:
            lines = f.read().splitlines(keepends=True)
        count = 0
        for i, line in enumerate(lines):
            body = line.rstrip("\r\n")
            key = body.strip()
            if key in pairs:
                indent = body[: len(body) - len(body.lstrip())]
                lines[i] = indent + pairs[key] + line[len(body) :]
                count += 1
        if count:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write("".join(lines))
            restored[path] = count
    return restored


def main(tag: str, russian: str, upstream: str) -> None:
    base = git("merge-base", russian, upstream).strip()
    squash = squash_translation(base, russian)
    mapping = translation_map(base, squash)

    git("checkout", "-q", "-B", f"ru/{tag}", f"refs/tags/{tag}")
    picked = subprocess.run(
        ["git", "cherry-pick", "--no-commit", "-X", "ours", squash],
        capture_output=True,
        text=True,
    )
    # Неразрешимые автоматически конфликты (файл удалён/переименован в оригинале):
    # оставляем версию оригинала.
    conflicted = list(
        filter(None, git("diff", "--name-only", "--diff-filter=U").split("\n"))
    )
    for path in conflicted:
        in_tag = subprocess.run(["git", "cat-file", "-e", f"HEAD:{path}"]).returncode
        if in_tag == 0:
            git("checkout", "HEAD", "--", path)
        else:
            git("rm", "-q", "-f", "--", path)
    if picked.returncode != 0 and not conflicted:
        sys.exit(f"cherry-pick failed:\n{picked.stderr}")

    restored = restore_lines(mapping)
    git("add", "-A")
    git("commit", "-q", "-m", f"Русская локализация (на основе {tag})")

    # Строки перевода, которые так и не попали в релиз (код в оригинале изменился).
    missing: dict[str, int] = {}
    for path, pairs in mapping.items():
        if not os.path.isfile(path):
            missing[path] = len(pairs)
            continue
        with open(path, encoding="utf-8") as f:
            present = {line.strip() for line in f}
        lost = sum(1 for a, b in pairs.items() if b not in present and a in present)
        if lost:
            missing[path] = lost

    with open("ru-report.md", "w", encoding="utf-8") as report:
        report.write(f"Русификация наложена на релиз `{tag}` оригинала.\n\n")
        total = sum(len(p) for p in mapping.values())
        report.write(f"- Строк перевода в словаре: {total}\n")
        report.write(
            f"- Восстановлено строк после переноса: {sum(restored.values())}\n"
        )
        if missing:
            report.write(
                "- Остались на английском (код в оригинале изменился):\n"
            )
            for path, n in sorted(missing.items()):
                report.write(f"  - `{path}`: {n}\n")
        if conflicted:
            report.write("- Файлы, где взята версия оригинала целиком:\n")
            for path in conflicted:
                report.write(f"  - `{path}`\n")
    print(open("ru-report.md", encoding="utf-8").read())


if __name__ == "__main__":
    main(*sys.argv[1:4])
