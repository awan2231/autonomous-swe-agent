from typing import TypedDict

from agent.llm import FixProposal
from agent.tools.github_client import IssueInfo


class AgentState(TypedDict, total=False):
    repo_name: str
    issue_number: int
    max_attempts: int
    issue: IssueInfo
    repo_path: str
    files: dict[str, str]
    test_result: dict
    proposal: FixProposal
    attempts: int
    last_error: str