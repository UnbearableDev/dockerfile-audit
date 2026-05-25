"""Smoke test for dockerfile-audit — direct call, bypassing Apify Standby + MCP transport."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dockerfile_audit import checks as registry
from dockerfile_audit.findings import summarize
from dockerfile_audit.parser import resolve_dockerfile_input


async def audit_file(label: str, path: Path) -> tuple[int, dict]:
    content = path.read_text()
    print(f"\n{'=' * 70}")
    print(f"FIXTURE: {label} ({path.name}, {len(content)} bytes)")
    print(f"{'=' * 70}")

    doc = await resolve_dockerfile_input(content, None)
    print(f"Parsed: {len(doc.instructions)} instructions, {len(doc.from_lines)} FROM")

    findings = registry.run_all(doc)
    summary = summarize(findings)
    print(f"\nSUMMARY: {summary['total_findings']} findings")
    print(f"  by severity: {summary['by_severity']}")
    print(f"  by category: {summary['by_category']}")
    print()

    for f in sorted(findings, key=lambda x: (
        -{"high": 3, "medium": 2, "low": 1, "info": 0}[x.severity],
        x.id,
        x.line_number or 0,
    )):
        line = f"L{f.line_number}" if f.line_number else "-"
        print(f"  [{f.severity.upper():6}] {f.id} ({line:>4}): {f.title}")

    return summary["total_findings"], summary


async def main():
    fixtures_dir = Path(__file__).resolve().parent

    bad_path = fixtures_dir / "bad-dockerfile"
    good_path = fixtures_dir / "good-dockerfile"

    if not bad_path.exists():
        print(f"FATAL: fixture not found at {bad_path}")
        return 1

    bad_count, bad_summary = await audit_file("BAD (every check should fire)", bad_path)
    good_count, good_summary = await audit_file("GOOD (clean dockerfile)", good_path)

    print("\n" + "=" * 70)
    print("EXPECTED FINDINGS ON BAD FIXTURE")
    print("=" * 70)
    expected_ids = [
        "DFA-001",  # nginx:latest
        "DFA-002",  # no digest pin
        "DFA-010",  # CMD shell form
        "DFA-012",  # MAINTAINER deprecated
        "DFA-013",  # ADD vs COPY
        "DFA-021",  # USER root
        "DFA-022",  # sudo
        "DFA-023",  # chmod 777
        "DFA-024",  # curl|bash
        "DFA-025",  # hardcoded ENV secret
        "DFA-030",  # apt-get update alone
        "DFA-031",  # apt install without --no-install-recommends
        "DFA-032",  # pip without --no-cache-dir
        "DFA-040",  # ARG SECRET_KEY
    ]

    doc = await resolve_dockerfile_input(bad_path.read_text(), None)
    findings = registry.run_all(doc)
    seen_ids = {f.id for f in findings}
    for eid in expected_ids:
        marker = "✓" if eid in seen_ids else "✗"
        print(f"  {marker} {eid}")

    miss = [eid for eid in expected_ids if eid not in seen_ids]
    extra = sorted(seen_ids - set(expected_ids) - {"DFA-027"})  # DFA-027 may also fire

    print(f"\nBad fixture: {bad_count} total findings (expected ~{len(expected_ids)}-20)")
    print(f"Good fixture: {good_count} total findings (expected 0-2)")
    print(f"Expected IDs hit: {len(expected_ids) - len(miss)}/{len(expected_ids)}")
    if miss:
        print(f"MISSING from bad: {miss}")
    if extra:
        print(f"Extras seen on bad: {extra}")

    print("\n" + "=" * 70)
    print("MCP SERVER TOOL REGISTRATION CHECK")
    print("=" * 70)
    from dockerfile_audit.main import get_server
    server = get_server()
    tools = await server.list_tools()
    print(f"Server: {server.name}")
    print(f"Tools registered: {len(tools)}")
    for t in tools:
        print(f"  - {t.name}")

    return 0 if not miss else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
