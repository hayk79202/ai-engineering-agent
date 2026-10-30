# AI Engineering Agent — Repository Inspector

An early developer-tool prototype that inspects a repository and returns structured JSON. This first version is a deterministic command-line tool; an MCP server and model-backed workflows are planned.

## Run

```bash
python inspect_repo.py /path/to/repository --output report.json
python inspect_repo.py .
```

Python 3.10+ is enough. The tool walks source files, counts files by extension, reports the largest files, and collects a capped list of `TODO` and `FIXME` markers. It skips common generated directories and never modifies the inspected repository.

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
repository path -> bounded file walk -> source inspection -> structured JSON report
```

The scan is bounded to 1,000 files, 1 MiB per file, and 50 markers. It does not run code or shell commands from the target repository. It currently handles repository metadata and source markers only. Future milestones are MCP tool exposure, log analysis, optional model summaries, schema validation, and workflow execution with explicit controls.

## License

MIT
