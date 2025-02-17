import subprocess
import sys


def run_tool(command: list[str]) -> int:
    return subprocess.call(command)


BLACK_CMD = ["black", "."]
MYPY_CMD = ["mypy", "trademeds"]
PYTEST_CMD = ["pytest"]


def format():
    sys.exit(run_tool(BLACK_CMD))


def check():
    sys.exit(run_tool(MYPY_CMD))


def test():
    sys.exit(run_tool(PYTEST_CMD))


def lint():
    tools = [
        BLACK_CMD,
        MYPY_CMD,
        PYTEST_CMD,
    ]

    for tool in tools:
        result = run_tool(tool)
        if result != 0:
            sys.exit(result)

    sys.exit(0)
