"""Read a bounded text log and summarize warnings and errors."""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

MAX_BYTES = 1024 * 1024
MAX_MATCHES = 20
SEVERITY = re.compile(r"\b(ERROR|WARN|WARNING)\b", re.IGNORECASE)


def analyze_log(path: Path) -> dict:
    if path.is_symlink():
        raise ValueError("symlink logs are not supported")
    path = path.resolve(strict=True)
    if not path.is_file():
        raise ValueError("path must be a file")
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("log exceeds 1 MiB limit")
    counts = Counter()
    matches = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for number, line in enumerate(lines, 1):
        match = SEVERITY.search(line)
        if match is None:
            continue
        severity = "warning" if match.group(1).upper().startswith("WARN") else "error"
        counts[severity] += 1
        if len(matches) < MAX_MATCHES:
            matches.append({"line": number, "severity": severity, "text": line[:200]})
    return {
        "path": str(path),
        "lines": len(lines),
        "counts": {"error": counts["error"], "warning": counts["warning"]},
        "matches": matches,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(analyze_log(args.path), indent=2))
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
