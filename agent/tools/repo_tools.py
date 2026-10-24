import ast
import os
import shutil
import subprocess
import sys
from pathlib import Path

IGNORE_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", ".pytest_cache"}
WORKSPACE = Path("workspace")


def clone_repo(clone_url: str, name: str) -> Path:
    """Clone a public repo into workspace/<name>, replacing any old copy."""
    dest = WORKSPACE / name
    if dest.exists():
        shutil.rmtree(dest)
    WORKSPACE.mkdir(exist_ok=True)
    subprocess.run(
        ["git", "clone", clone_url, str(dest)],
        check=True, capture_output=True, text=True,
    )
    return dest


def list_files(repo_path: Path) -> list[str]:
    """Return all file paths in the repo, relative to its root."""
    files = []
    for root, dirs, filenames in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in filenames:
            files.append(str(Path(root, f).relative_to(repo_path)))
    return sorted(files)


def read_file(repo_path: Path, rel_path: str) -> str:
    """Read a file, refusing paths that escape the repo folder."""
    full = (repo_path / rel_path).resolve()
    if not full.is_relative_to(repo_path.resolve()):
        raise ValueError("Path is outside the repository")
    return full.read_text(encoding="utf-8")


def outline_python_file(source: str) -> list[dict]:
    """Use AST parsing to list every function and class with line numbers."""
    tree = ast.parse(source)
    items = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            items.append({
                "type": "class" if isinstance(node, ast.ClassDef) else "function",
                "name": node.name,
                "start_line": node.lineno,
                "end_line": node.end_lineno,
                "docstring": ast.get_docstring(node),
            })
    return sorted(items, key=lambda i: i["start_line"])


def search_code(repo_path: Path, keyword: str) -> list[str]:
    """Find every line containing the keyword, as file:line: text."""
    results = []
    for rel in list_files(repo_path):
        try:
            text = read_file(repo_path, rel)
        except UnicodeDecodeError:
            continue  # skip binary files
        for i, line in enumerate(text.splitlines(), start=1):
            if keyword in line:
                results.append(f"{rel}:{i}: {line.strip()}")
    return results


if __name__ == "__main__":
    # Usage: python3 -m agent.tools.repo_tools owner/repo
    repo_name = sys.argv[1]
    path = clone_repo(f"https://github.com/{repo_name}.git", repo_name.split("/")[1])

    print("FILES:")
    for f in list_files(path):
        print(" ", f)

    print("\nOUTLINE of calculator.py:")
    for item in outline_python_file(read_file(path, "calculator.py")):
        print(f"  {item['type']} {item['name']} (lines {item['start_line']}-{item['end_line']})")

    print("\nSEARCH 'divide':")
    for hit in search_code(path, "divide"):
        print(" ", hit)