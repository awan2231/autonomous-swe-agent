# Autonomous AI Software Engineer

I built an AI agent that reads a GitHub issue, explores the codebase, edits files, and runs the tests inside a Docker sandbox. When the tests fail, it reads the failure output and tries again until they pass. When it succeeds, it can open a pull request with the fix.

It is built with LangGraph, Google Gemini, Python AST parsing, Docker, and the GitHub API.

## How it works

```
START → fetch_issue → run_tests ──passed──────────→ END
                          │  ↑
                          │  └──── apply_edits ← propose_fix
                          └─ failed and attempts left ─┘
                          └─ failed, no attempts left → END
```

1. **Fetch issue:** I read the issue title, body, and comments from GitHub and clone the repository.
2. **Run tests:** pytest runs inside an isolated Docker container with no network access and a 512 MB memory limit, so code from other repositories never runs directly on my machine.
3. **Propose fix:** the LLM receives the issue, the source files, and the latest test output. It returns structured edits made of a file path, the exact old text, and the new text.
4. **Apply edits:** an edit is applied only if the old text appears exactly once in the file. Anything else is rejected, and the error is sent back to the model.
5. **Retry loop:** the tests run again. If they still fail, the new output goes back to the LLM for another attempt, up to a set limit.
6. **Open a pull request (optional):** the agent creates a branch, commits the changes, and opens a pull request that references the issue.

The AST tools in `agent/tools/repo_tools.py` use Python's `ast` module to list every function and class in a file with its line numbers.

## Project structure

```
agent/
├── graph.py        # LangGraph workflow
├── nodes.py        # graph nodes and routing logic
├── state.py        # shared agent state
├── llm.py          # Gemini client and structured fix proposals
├── prompts.py      # system prompt
├── main.py         # command-line entry point
└── tools/
    ├── github_client.py   # reads GitHub issues
    ├── repo_tools.py      # clone, list, read, search, AST outline
    ├── edit_tools.py      # safe exact-match file edits
    ├── test_runner.py     # runs pytest in the Docker sandbox
    └── pr_tools.py        # creates the branch, commit, and pull request
sandbox/Dockerfile          # test environment image
evaluation/                 # benchmark cases and evaluation harness
```

## Setup

You need Python 3.11 or newer, Docker Desktop, a Google Gemini API key, and a GitHub token.

```bash
git clone https://github.com/awan2231/autonomous-ai-software-engineer.git
cd autonomous-ai-software-engineer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
docker build -t swe-agent-sandbox sandbox/
```

Open `.env` and add your own keys. For the GitHub token, use either a classic token with the `repo` scope, or a fine-grained token with Contents and Pull requests set to read and write.

## Usage

Docker Desktop must be running.

Fix an issue:

```bash
python3 -m agent.main owner/repo 1
```

Fix an issue and open a pull request:

```bash
python3 -m agent.main owner/repo 1 --pr
```

I used [demo-buggy-repo](https://github.com/awan2231/demo-buggy-repo) as my test target. It contains a `divide()` function with a deliberate bug and a failing test.

## Evaluation

I wrote a benchmark of 5 small buggy Python projects, each with an issue description and a test suite:

```bash
python3 -m evaluation.make_cases
python3 -m evaluation.run_eval
```

The harness reports the success rate and the number of attempts for each case. It also marks a case as failed if the agent edited the test files, since rewriting a test to make it pass is not a real fix.

**Result:** 5 out of 5 cases solved, with an average of 1.0 attempts.

These cases are small, single-file bugs, so this is a sanity check and not a measure of how the agent performs on large real-world repositories.

## Limitations

- It only supports Python projects that use pytest.
- It sends whole source files to the LLM, so large repositories would need smarter file selection.
- The AST outline is available as a tool, but the agent does not yet use it to decide which files to read.
- Fixes are verified only by the existing tests, so a weak test suite can let a wrong fix through.
- It can only clone public repositories.

## Possible next steps

- Use the AST outline to pick the relevant files before calling the LLM.
- Test the agent on real open-source issues.
- Add support for more languages and test frameworks.