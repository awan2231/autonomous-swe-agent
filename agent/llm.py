import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from agent.prompts import SYSTEM_PROMPT
from agent.tools.github_client import IssueInfo

load_dotenv()


class FileEdit(BaseModel):
    file_path: str = Field(description="Path of the file, relative to the repo root")
    old_str: str = Field(description="Exact existing text to replace; must appear exactly once")
    new_str: str = Field(description="Replacement text")


class FixProposal(BaseModel):
    reasoning: str = Field(description="Short explanation of the root cause and the fix")
    edits: list[FileEdit]


def get_llm():
    return ChatGoogleGenerativeAI(
        model=os.getenv("MODEL_NAME", "gemini-3.8-flash"),
        temperature=0,
    )


def build_context(
    issue: IssueInfo,
    files: dict[str, str],
    test_output: str | None = None,
    max_chars: int = 30000,
) -> str:
    parts = [f"ISSUE #{issue.number}: {issue.title}\n{issue.body}"]
    if issue.comments:
        parts.append("COMMENTS:\n" + "\n".join(issue.comments))

    parts.append("REPOSITORY FILES:")
    used = 0
    for path, content in files.items():
        block = f"\n--- {path} ---\n{content}"
        if used + len(block) > max_chars:
            parts.append(f"\n(skipped {path}: too large)")
            continue
        used += len(block)
        parts.append(block)

    if test_output:
        parts.append(f"\nLATEST TEST OUTPUT:\n{test_output}")
    return "\n".join(parts)


def propose_fix(
    issue: IssueInfo, files: dict[str, str], test_output: str | None = None
) -> FixProposal:
    llm = get_llm().with_structured_output(FixProposal)
    return llm.invoke([
        ("system", SYSTEM_PROMPT),
        ("human", build_context(issue, files, test_output)),
    ])