import subprocess
import sys

from agent.graph import build_graph


def main(repo_name: str, issue_number: int, max_attempts: int = 3) -> dict:
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
    return final


if __name__ == "__main__":
    # Usage: python3 -m agent.main owner/repo issue_number
    main(sys.argv[1], int(sys.argv[2]))