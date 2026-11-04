from pathlib import Path
from urllib.parse import quote

README = Path(__file__).parent / "README.md"
ROOT = README.parent

START = "<!-- TOC START -->"
END = "<!-- TOC END -->"

# Never list these files in the TOC (case-insensitive).
EXCLUDE_NAMES = {
    Path(__file__).name.lower(),  # this script, e.g. "generate_toc.py"
    "readme.md",                  # README.md / readme.md / ReadMe.md ...
}

# Directories that are never scanned (hidden dirs are skipped too)
SKIP_DIRS = {".git", ".hg", ".svn", "__pycache__", ".venv", "venv", "node_modules"}


def collect_files(root: Path) -> list[Path]:
    """Return every non-hidden file under *root*, excluding README and this script."""
    files = []
    for p in root.rglob("*"):
        rel = p.relative_to(root)
        if any(part in SKIP_DIRS or part.startswith(".") for part in rel.parts):
            continue
        if not p.is_file():
            continue
        if p.name.lower() in EXCLUDE_NAMES:
            continue
        files.append(p)
    return files


def build_tree(files: list[Path], root: Path) -> dict:
    """Nested dict: {name: subtree} for folders, {name: None} for files."""
    tree: dict = {}
    for f in files:
        *folders, name = f.relative_to(root).parts
        node = tree
        for folder in folders:
            node = node.setdefault(folder, {})
        node[name] = None
    return tree


def render_tree(node: dict, prefix: str = "", depth: int = 0) -> list[str]:
    """Render the tree as a nested Markdown list; folders first, then files."""
    dirs = sorted((k for k, v in node.items() if isinstance(v, dict)), key=str.lower)
    files = sorted((k for k, v in node.items() if v is None), key=str.lower)

    lines = []
    indent = "  " * depth

    for d in dirs:
        lines.append(f"{indent}- **{d}/**")
        lines.extend(render_tree(node[d], f"{prefix}{d}/", depth + 1))

    for f in files:
        lines.append(f"{indent}- [{f}]({quote(prefix + f)})")

    return lines


def main() -> None:
    files = collect_files(ROOT)
    toc = "\n".join(render_tree(build_tree(files, ROOT)))

    content = README.read_text(encoding="utf-8")

    if START not in content or END not in content:
        raise ValueError("TOC markers not found in README.md")

    before, remainder = content.split(START, 1)
    _, after = remainder.split(END, 1)

    README.write_text(
        before + START + "\n" + toc + "\n" + END + after,
        encoding="utf-8",
    )

    print(f"TOC updated: {len(files)} files.")


if __name__ == "__main__":
    main()