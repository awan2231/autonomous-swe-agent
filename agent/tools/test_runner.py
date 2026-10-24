import sys
from pathlib import Path

import docker

from agent.tools.repo_tools import clone_repo

IMAGE = "swe-agent-sandbox"


def run_tests(repo_path: Path, timeout: int = 120) -> dict:
    """Run pytest inside an isolated container and return the result."""
    client = docker.from_env()
    container = client.containers.run(
        IMAGE,
        command="pytest -q --tb=short -p no:cacheprovider",
        volumes={str(repo_path.resolve()): {"bind": "/repo", "mode": "rw"}},
        working_dir="/repo",
        network_disabled=True,
        mem_limit="512m",
        detach=True,
    )
    try:
        exit_code = container.wait(timeout=timeout)["StatusCode"]
        output = container.logs().decode("utf-8", errors="replace")
    except Exception:
        exit_code = -1
        output = f"Test run failed or timed out after {timeout}s"
    finally:
        container.remove(force=True)
    return {"passed": exit_code == 0, "exit_code": exit_code, "output": output}


if __name__ == "__main__":
    # Usage: python3 -m agent.tools.test_runner owner/repo
    repo_name = sys.argv[1]
    path = clone_repo(f"https://github.com/{repo_name}.git", repo_name.split("/")[1])
    result = run_tests(path)
    print("PASSED" if result["passed"] else "FAILED")
    print(result["output"])