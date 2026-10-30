# AI Engineering Agent — Repository Inspector

![Python tests](https://github.com/hayk79202/ai-engineering-agent/actions/workflows/ci.yml/badge.svg)

A read-only developer tool with two MCP tools: repository inspection and log analysis. It returns JSON reports and keeps MCP access inside a configured workspace. Model-backed reasoning is a future extension; the current analysis is deterministic.

## Run

```bash
python inspect_repo.py /path/to/repository --output report.json
python inspect_repo.py .
python analyze_log.py examples/sample.log
```

The standalone CLIs use Python 3.10+ and have no third-party dependencies. The repository tool counts source files, reports the largest files, and collects a capped list of `TODO` and `FIXME` comments. The log tool counts warning and error lines. Both are read-only.

## MCP server

```bash
python -m pip install -r requirements.txt
python server.py
```

Configure your MCP client to launch `python server.py` over stdio, with `ENGINEERING_ROOT` set to the repository or workspace you want it to inspect. The server exposes `inspect_repository(path)` and `analyze_log_file(path)`. Relative paths resolve from that root; paths outside it are rejected. The default root is the server's current working directory.

The server waits for an MCP client on standard input; it does not print a startup page.

Run `python -m unittest discover -s tests -v` to exercise both tools, including an in-process MCP call. GitHub Actions runs these checks on each push.

## Example result

```json
{
  "root": "/absolute/path/to/repository",
  "files_scanned": 12,
  "extensions": {".py": 8, ".md": 4},
  "largest_files": [],
  "markers": []
}
```

The values above illustrate the response shape; they are not a measurement of this repository.

## Design

```text
MCP client -> workspace boundary -> bounded scan -> JSON report
```

The repository scan is bounded to 1,000 files, 1 MiB per file, and 50 markers. Log analysis reads at most 1 MiB and returns at most 20 matching lines. Neither tool runs code or shell commands from the target repository. Future milestones include optional model summaries and workflow execution with explicit controls.

## License

MIT
