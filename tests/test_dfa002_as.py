"""Targeted tests for DFA-002 with multi-stage AS alias.

Verifies the digest snippet places @sha256:<digest> BEFORE the alias, not after.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dockerfile_audit import checks as registry
from dockerfile_audit.parser import resolve_dockerfile_input


async def _audit(content: str):
    doc = await resolve_dockerfile_input(content, None)
    return registry.run_all(doc)


def _dfa002_snippet(findings):
    for f in findings:
        if f.id == "DFA-002":
            return f.fix_dockerfile_snippet
    return None


async def main():
    cases = [
        (
            "no AS clause",
            "FROM ubuntu:latest\nUSER 10001\n",
            "FROM ubuntu:latest@sha256:<digest>",
        ),
        (
            "uppercase AS",
            "FROM ubuntu:latest AS builder\nUSER 10001\n",
            "FROM ubuntu:latest@sha256:<digest> AS builder",
        ),
        (
            "lowercase as",
            "FROM ubuntu:latest as builder\nUSER 10001\n",
            "FROM ubuntu:latest@sha256:<digest> as builder",
        ),
        (
            "registry prefix + AS",
            "FROM gcr.io/distroless/python:latest AS runtime\nUSER 10001\n",
            "FROM gcr.io/distroless/python:latest@sha256:<digest> AS runtime",
        ),
        (
            "no tag, with AS",
            "FROM ubuntu AS builder\nUSER 10001\n",
            "FROM ubuntu@sha256:<digest> AS builder",
        ),
    ]
    failed = 0
    for label, dockerfile, expected in cases:
        findings = await _audit(dockerfile)
        got = _dfa002_snippet(findings)
        ok = got == expected
        marker = "PASS" if ok else "FAIL"
        print(f"  [{marker}] {label}")
        if not ok:
            print(f"    expected: {expected!r}")
            print(f"    got:      {got!r}")
            failed += 1

    # No-fire case: digest already present
    digest_case = "FROM ubuntu:latest@sha256:deadbeef AS builder\nUSER 10001\n"
    findings = await _audit(digest_case)
    has_dfa002 = any(f.id == "DFA-002" for f in findings)
    if has_dfa002:
        print("  [FAIL] digest-present case should NOT fire DFA-002 - but it did")
        failed += 1
    else:
        print("  [PASS] digest-present case correctly skipped")

    if failed:
        print(f"\n{failed} test(s) failed")
        return 1
    print("\nAll DFA-002 AS-alias tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
