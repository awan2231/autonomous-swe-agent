from pathlib import Path

from agent.llm import propose_fix
from agent.state import AgentState
from agent.tools.edit_tools import apply_edit
from agent.tools.github_client import GitHubClient
from agent.tools.repo_tools import clone_repo, list_files, read_file
from agent.tools.test_runner import run_tests


def load_py_files(repo_path: Path) -> dict[str, str]:
    return {p: read_file(repo_path, p) for p in list_files(repo_path) if p.endswith(".py")}


def fetch_issue_node(state: AgentState) -> dict:
    issue = GitHubClient().get_issue(state["repo_name"], state["issue_number"])
    repo_path = clone_repo(issue.clone_url, state["repo_name"].split("/")[1])
    print(f"Fetched issue #{issue.number}: {issue.title}")
    return {"issue": issue, "repo_path": str(repo_path), "attempts": 0, "last_error": ""}


def run_tests_node(state: AgentState) -> dict:
    repo_path = Path(state["repo_path"])
    result = run_tests(repo_path)
    print(f"Tests: {'PASSED' if result['passed'] else 'FAILED'}")
    # reload files so the LLM always sees the current code, including earlier edits
    return {"test_result": result, "files": load_py_files(repo_path)}


def propose_fix_node(state: AgentState) -> dict:
    attempt = state["attempts"] + 1
    print(f"\nAttempt {attempt}/{state['max_attempts']}: asking the LLM for a fix...")

    feedback = state["test_result"]["output"]
    if state.get("last_error"):
        feedback += f"\n\nYour previous edit could not be applied: {state['last_error']}"

    proposal = propose_fix(state["issue"], state["files"], feedback)
    print("Reasoning:", proposal.reasoning)
    return {"proposal": proposal, "attempts": attempt}


def apply_edits_node(state: AgentState) -> dict:
    repo_path = Path(state["repo_path"])
    try:
        for edit in state["proposal"].edits:
            apply_edit(repo_path, edit.file_path, edit.old_str, edit.new_str)
            print(f"Edited {edit.file_path}")
    except Exception as e:
        print(f"Edit failed: {e}")
        return {"last_error": str(e)}
    return {"last_error": ""}


def route_after_tests(state: AgentState) -> str:
    if state["test_result"]["passed"]:
        return "done"
    if state["attempts"] >= state["max_attempts"]:
        return "give_up"
    return "retry"