import sys

from agent.llm import propose_fix
from agent.tools.edit_tools import apply_edit
from agent.tools.github_client import GitHubClient
from agent.tools.repo_tools import clone_repo, list_files, read_file
from agent.tools.test_runner import run_tests


def main(repo_name: str, issue_number: int) -> None:
    issue = GitHubClient().get_issue(repo_name, issue_number)
    repo_path = clone_repo(issue.clone_url, repo_name.split("/")[1])
    files = {p: read_file(repo_path, p) for p in list_files(repo_path) if p.endswith(".py")}

    before = run_tests(repo_path)
    print("Before:", "PASSED" if before["passed"] else "FAILED")

    proposal = propose_fix(issue, files, before["output"])
    print("\nReasoning:", proposal.reasoning)

    for edit in proposal.edits:
        apply_edit(repo_path, edit.file_path, edit.old_str, edit.new_str)
        print(f"Edited {edit.file_path}")

    after = run_tests(repo_path)
    print("\nAfter:", "PASSED" if after["passed"] else "FAILED")
    print(after["output"])


if __name__ == "__main__":
    # Usage: python3 -m agent.demo_fix owner/repo issue_number
    main(sys.argv[1], int(sys.argv[2]))