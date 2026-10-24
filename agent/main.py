import subprocess
import sys
from pathlib import Path

from agent.graph import build_graph
from agent.tools.pr_tools import open_pull_request


def main(repo_name: str, issue_number: int, max_attempts: int = 3, open_pr: bool = False) -> dict:
    app = build_graph()
    final = app.invoke({
        "repo_name": repo_name,
        "issue_number": issue_number,
        "max_attempts": max_attempts,
    })

    passed = final["test_result"]["passed"]
    print("\n" + "=" * 50)
    if passed and final["attempts"] == 0:
        print("Tests already pass, nothing to fix.")
    elif passed:
        print(f"FIXED in {final['attempts']} attempt(s)")
    else:
        print(f"NOT FIXED after {final['attempts']} attempt(s)")

    diff = subprocess.run(
        ["git", "-C", final["repo_path"], "diff"],
        capture_output=True, text=True,
    ).stdout
    print("\nCHANGES MADE:\n" + (diff or "(none)"))

    if open_pr and passed and final["attempts"] > 0:
        url = open_pull_request(
            repo_name, final["issue"], Path(final["repo_path"]), final["proposal"].reasoning
        )
        print(f"\nPull request opened: {url}")
    return final


if __name__ == "__main__":
    # Usage: python3 -m agent.main owner/repo issue_number [--pr]
    main(sys.argv[1], int(sys.argv[2]), open_pr="--pr" in sys.argv)