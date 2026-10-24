import hashlib
import json
import shutil
import time
from pathlib import Path

from agent.graph import build_graph
from agent.tools.github_client import IssueInfo

CASES_DIR = Path("evaluation/cases")
WORK_DIR = Path("workspace/eval")
MAX_ATTEMPTS = 3


def load_issue(case_dir: Path, number: int) -> IssueInfo:
    lines = (case_dir / "issue.md").read_text(encoding="utf-8").splitlines()
    return IssueInfo(
        repo_name=f"local/{case_dir.name}",
        number=number,
        title=lines[0].lstrip("# ").strip(),
        body="\n".join(lines[1:]).strip(),
    )


def hash_tests(repo_path: Path) -> dict[str, str]:
    return {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in repo_path.glob("test_*.py")
    }


def run_case(app, case_dir: Path, number: int) -> dict:
    repo_path = WORK_DIR / case_dir.name
    if repo_path.exists():
        shutil.rmtree(repo_path)
    shutil.copytree(case_dir, repo_path)

    tests_before = hash_tests(repo_path)
    start = time.time()
    try:
        final = app.invoke({
            "repo_name": f"local/{case_dir.name}",
            "issue_number": number,
            "max_attempts": MAX_ATTEMPTS,
            "issue": load_issue(case_dir, number),
            "repo_path": str(repo_path),
        })
        passed = final["test_result"]["passed"]
        attempts = final["attempts"]
        error = ""
    except Exception as e:
        passed, attempts, error = False, 0, str(e)[:200]

    tampered = hash_tests(repo_path) != tests_before
    return {
        "case": case_dir.name,
        "passed": passed and not tampered,
        "attempts": attempts,
        "seconds": round(time.time() - start, 1),
        "tests_modified": tampered,
        "error": error,
    }


def main():
    app = build_graph()
    case_dirs = sorted(d for d in CASES_DIR.iterdir() if d.is_dir())
    results = []

    for i, case_dir in enumerate(case_dirs, start=1):
        print(f"\n### Case {i}/{len(case_dirs)}: {case_dir.name}")
        result = run_case(app, case_dir, i)
        results.append(result)
        print(f"-> {'PASS' if result['passed'] else 'FAIL'}")

    print("\n" + "=" * 60)
    print(f"{'CASE':<15}{'RESULT':<10}{'ATTEMPTS':<10}{'SECONDS':<10}NOTES")
    for r in results:
        notes = "edited tests!" if r["tests_modified"] else r["error"]
        print(f"{r['case']:<15}{'PASS' if r['passed'] else 'FAIL':<10}"
              f"{r['attempts']:<10}{r['seconds']:<10}{notes}")

    solved = [r for r in results if r["passed"]]
    print(f"\nSuccess rate: {len(solved)}/{len(results)} ({100 * len(solved) // len(results)}%)")
    if solved:
        avg = sum(r["attempts"] for r in solved) / len(solved)
        print(f"Average attempts on solved cases: {avg:.1f}")

    Path("evaluation/results.json").write_text(json.dumps(results, indent=2))
    print("Saved evaluation/results.json")


if __name__ == "__main__":
    main()