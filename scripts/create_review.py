from pathlib import Path

from bot.caches.paths import Paths


IGNORE = {".git", ".idea", ".ruff_cache", ".venv", "__pycache__", "backups"}

tree, files = [], []


def walk(path: Path, prefix: str = "") -> None:
    paths = sorted(
        (p for p in path.iterdir() if p.name not in IGNORE),
        key=lambda p: (p.is_file(), p.name.lower()),
    )

    for i, p in enumerate(paths, 1):
        tree.append(f"{prefix}{'└── ' if i == len(paths) else '├── '}{p.name}")

        if p.is_dir():
            walk(p, prefix + ("    " if i == len(paths) else "│   "))
        elif p.suffix in {".py", ".ini", ".yaml", ".conf", ".toml"} or p.stem == "Dockerfile":
            with open(p, encoding="utf-8") as f:
                files.append(f"# {'=' * 77}\n# {p.relative_to(root).as_posix()}\n\n{f.read()}")


if __name__ == "__main__":
    root = Paths.ROOT
    walk(root)

    with open("all_in_one.txt", "w", encoding="utf-8") as file:
        file.write("\n".join([*tree, "", *files]))
