import json
import re
from collections import Counter
from pathlib import Path

LOG_PATH = Path("/app/access.log")
REPORT_PATH = Path("/app/report.json")
REQUEST_RE = re.compile(r'^([^\s]+)\s+.*?"[A-Z]+\s+(\S+)\s+HTTP/[^\s]+"')


def main() -> None:
    total_requests = 0
    ips: set[str] = set()
    paths: Counter[str] = Counter()

    for raw_line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue
        match = REQUEST_RE.match(raw_line)
        if match is None:
            raise ValueError(f"Unsupported access-log entry: {raw_line!r}")
        ip_address, path = match.groups()
        total_requests += 1
        ips.add(ip_address)
        paths[path] += 1

    if not paths:
        raise ValueError("The access log contains no requests")

    highest_count = max(paths.values())
    report = {
        "total_requests": total_requests,
        "unique_ips": len(ips),
        "top_path": min(path for path, count in paths.items() if count == highest_count),
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
