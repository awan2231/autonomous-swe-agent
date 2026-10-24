from pathlib import Path


def apply_edit(repo_path: Path, file_path: str, old_str: str, new_str: str) -> None:
    """Replace old_str with new_str in a file. old_str must appear exactly once."""
    full = (repo_path / file_path).resolve()
    if not full.is_relative_to(repo_path.resolve()):
        raise ValueError("Path is outside the repository")

    text = full.read_text(encoding="utf-8")
    count = text.count(old_str)
    if count != 1:
        raise ValueError(f"old_str found {count} times in {file_path}; it must appear exactly once")

    full.write_text(text.replace(old_str, new_str, 1), encoding="utf-8")