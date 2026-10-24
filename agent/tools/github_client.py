import os
import sys
from dataclasses import dataclass, field

from dotenv import load_dotenv
from github import Auth, Github

load_dotenv()


@dataclass
class IssueInfo:
    repo_name: str
    number: int
    title: str
    body: str
    labels: list[str] = field(default_factory=list)
    comments: list[str] = field(default_factory=list)
    clone_url: str = ""
    default_branch: str = "main"


class GitHubClient:
    def __init__(self, token: str | None = None):
        token = token or os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("GITHUB_TOKEN is not set. Add it to your .env file.")
        self.gh = Github(auth=Auth.Token(token))

    def get_issue(self, repo_name: str, issue_number: int) -> IssueInfo:
        repo = self.gh.get_repo(repo_name)
        issue = repo.get_issue(number=issue_number)
        comments = [f"{c.user.login}: {c.body}" for c in issue.get_comments()]
        return IssueInfo(
            repo_name=repo_name,
            number=issue.number,
            title=issue.title,
            body=issue.body or "",
            labels=[label.name for label in issue.labels],
            comments=comments,
            clone_url=repo.clone_url,
            default_branch=repo.default_branch,
        )


if __name__ == "__main__":
    # Usage: python3 -m agent.tools.github_client owner/repo 1
    repo_name, number = sys.argv[1], int(sys.argv[2])
    info = GitHubClient().get_issue(repo_name, number)
    print(f"#{info.number}: {info.title}")
    print(f"Body: {info.body}")
    print(f"Labels: {info.labels}")
    print(f"Comments: {info.comments}")
    print(f"Clone URL: {info.clone_url}")