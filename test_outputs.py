"""Verifier tests for the log-report task."""

import json
import re
from collections import Counter
from pathlib import Path

LOG_PATH = Path("/app/access.log")
REPORT_PATH = Path("/app/report.json")
REQUEST_RE = re.compile(r'^([^\s]+)\s+.*?"[A-Z]+\s+(\S+)\s+HTTP/[^\s]+"')
REQUIRED_KEYS = {"total_requests", "unique_ips", "top_path"}


def load_report() -> dict:
    assert REPORT_PATH.is_file(), "Missing required output file: /app/report.json"
    try:
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AssertionError("/app/report.json must contain valid UTF-8 JSON") from exc
    assert isinstance(report, dict), "/app/report.json must contain a JSON object"
    return report


def expected_values() -> dict:
    total_requests = 0
    unique_ips: set[str] = set()
    path_counts: Counter[str] = Counter()
    for raw_line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue
        match = REQUEST_RE.match(raw_line)
        assert match is not None, f"Invalid task fixture log entry: {raw_line!r}"
        ip_address, path = match.groups()
        total_requests += 1
        unique_ips.add(ip_address)
        path_counts[path] += 1
    assert path_counts, "The task fixture must contain at least one request"
    highest_count = max(path_counts.values())
    return {
        "total_requests": total_requests,
        "unique_ips": len(unique_ips),
        "top_path": min(path for path, count in path_counts.items() if count == highest_count),
    }


def test_success_criterion_1_report_schema():
    """Verifies instruction.md success criterion 1: exact JSON schema and types."""
    report = load_report()
    assert set(report) == REQUIRED_KEYS, (
        "report.json must contain exactly total_requests, unique_ips, and top_path"
    )
    assert type(report["total_requests"]) is int, "total_requests must be an integer"
    assert type(report["unique_ips"]) is int, "unique_ips must be an integer"
    assert isinstance(report["top_path"], str), "top_path must be a string"


def test_success_criterion_2_total_requests():
    """Verifies instruction.md success criterion 2: total request count."""
    assert load_report()["total_requests"] == expected_values()["total_requests"], (
        "total_requests does not match non-empty log entries"
    )


def test_success_criterion_3_unique_ips():
    """Verifies instruction.md success criterion 3: distinct client IP count."""
    assert load_report()["unique_ips"] == expected_values()["unique_ips"], (
        "unique_ips does not match distinct client IP addresses"
    )


def test_success_criterion_4_top_path():
    """Verifies instruction.md success criterion 4: most frequent path and tie-break."""
    assert load_report()["top_path"] == expected_values()["top_path"], (
        "top_path does not match the most frequent request path"
    )
