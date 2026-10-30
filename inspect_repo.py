"""Bounded, read-only repository inspection that emits JSON."""
import argparse
import json
import os
import re
from collections import Counter
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "node_modules", "dist", "build", "__pycache__"}
COMMENT_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx", ".cpp", ".hpp", ".h", ".c"}
MARKER = re.compile(r"(?:#|//|/\*|\*)\s*(?:TODO|FIXME)\b", re.IGNORECASE)
MAX_FILES = 1000
MAX_BYTES = 1024 * 1024
MAX_MARKERS = 50


def inspect(root: Path) -> dict:
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("path must be a directory")
    files = []
    extensions = Counter()
    markers = []
    for directory, subdirs, names in os.walk(root):
        subdirs[:] = sorted(name for name in subdirs if name not in SKIP_DIRS)
        for name in sorted(names):
            if len(files) >= MAX_FILES:
                break
            path = Path(directory) / name
            if path.is_symlink() or not path.is_file():
                continue
            try:
                size = path.stat().st_size
            except OSError:
                continue
            relative = path.relative_to(root).as_posix()
            files.append({"path": relative, "bytes": size})
            extensions[path.suffix.lower() or "(none)"] += 1
            if size > MAX_BYTES or path.suffix.lower() not in COMMENT_EXTENSIONS or len(markers) >= MAX_MARKERS:
                continue
            try:
                for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    if MARKER.search(line):
                        markers.append({"path": relative, "line": number, "text": line.strip()[:160]})
                        if len(markers) >= MAX_MARKERS:
                            break
            except (OSError, UnicodeError):
                pass
        if len(files) >= MAX_FILES:
            break
    return {
        "root": str(root),
        "files_scanned": len(files),
        "scan_limit_reached": len(files) >= MAX_FILES,
        "extensions": dict(sorted(extensions.items())),
        "largest_files": sorted(files, key=lambda item: item["bytes"], reverse=True)[:5],
        "markers": markers,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = inspect(args.path)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    payload = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
