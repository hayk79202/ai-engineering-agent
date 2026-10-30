"""Read-only MCP server for repository and log inspection."""
import os
from pathlib import Path

from mcp.server import MCPServer

from analyze_log import analyze_log
from inspect_repo import inspect

mcp = MCPServer("Engineering Inspector")


def allowed_path(path: str) -> Path:
    root = Path(os.environ.get("ENGINEERING_ROOT", ".")).resolve(strict=True)
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = candidate.resolve(strict=True)
    if not candidate.is_relative_to(root):
        raise ValueError("path must be inside ENGINEERING_ROOT")
    return candidate


@mcp.tool()
def inspect_repository(path: str = ".") -> dict:
    """Summarize source files and TODO markers inside the configured workspace."""
    return inspect(allowed_path(path))


@mcp.tool()
def analyze_log_file(path: str) -> dict:
    """Count error and warning lines in a text log inside the workspace."""
    return analyze_log(allowed_path(path))


if __name__ == "__main__":
    mcp.run()
