# Dockerfile Security & Quality Audit

> Hadolint-grade Dockerfile audit as an MCP server. 18+ checks across 5 categories, every finding ships with severity, line number, remediation text, and a copy-paste Dockerfile snippet.

**Built by [Unbearable Labs](https://github.com/UnbearableDev).** Pay-per-event pricing — only billed when a tool is actually called.

---

## Available on

- [Apify Actor Store](https://apify.com/unbearable_dev/dockerfile-audit) — primary, metered usage (PPE)
- MCPize — *pending submission*
- MCP.so — *pending submission*
- PulseMCP — *pending submission*
- Smithery — *pending submission*
- Glama — *pending submission*

**Newsletter:** [Unbearable TechTips Weekly](https://unbearabletechtips.com) · **All Actors:** [github.com/UnbearableDev](https://github.com/UnbearableDev)

## What it does

Point any MCP-capable client (Claude Desktop, Cursor, n8n, Make, Zapier, custom agents) at this server, hand it a Dockerfile, get back a structured report:

- **Severity** — high / medium / low / info
- **Line number** — exact location in the file
- **Description** — what's wrong and why it matters
- **Remediation** — what to do about it
- **Fix snippet** — Dockerfile syntax you can paste directly

## Tools

| Tool | Purpose |
|------|---------|
| `audit_dockerfile(dockerfile_content? \| dockerfile_url?, min_severity='low')` | Run all checks |
| `check_base_image(...)` | FROM/tag/digest/registry checks only |
| `check_instructions(...)` | CMD form, ADD vs COPY, MAINTAINER, etc. |
| `check_security(...)` | USER, sudo, chmod 777, curl\|bash, hardcoded secrets, HEALTHCHECK |
| `check_efficiency(...)` | apt cache hygiene, pip caching |
| `check_secrets(...)` | ARG with secret-pattern names |
| `list_checks(category?)` | Browse the full check catalog |

Provide exactly one of `dockerfile_content` (paste the file) or `dockerfile_url` (HTTPS URL — e.g. GitHub raw).

## Check catalog (v1: 18 checks across 5 categories)

| ID | Category | Severity | Title |
|----|----------|----------|-------|
| DFA-001 | base_image | medium | Image uses :latest tag or no tag |
| DFA-002 | base_image | info | No SHA256 digest pin on FROM |
| DFA-003 | base_image | medium | Untrusted registry |
| DFA-010 | instructions | low | CMD in shell form |
| DFA-011 | instructions | low | ENTRYPOINT in shell form |
| DFA-012 | instructions | info | MAINTAINER instruction is deprecated |
| DFA-013 | instructions | medium | ADD used where COPY would suffice |
| DFA-020 | security | medium | No USER directive (runs as root) |
| DFA-021 | security | high | USER root set explicitly |
| DFA-022 | security | high | sudo invoked in RUN |
| DFA-023 | security | high | chmod 777 in RUN |
| DFA-024 | security | medium | curl\|bash pattern in RUN |
| DFA-025 | security | high | Hardcoded secret in ENV |
| DFA-027 | security | low | No HEALTHCHECK |
| DFA-030 | efficiency | low | apt-get update without install |
| DFA-031 | efficiency | low | apt-get install without --no-install-recommends |
| DFA-032 | efficiency | low | pip install without --no-cache-dir |
| DFA-040 | secrets | medium | ARG with secret-pattern name |

Use `list_checks` to get the canonical, up-to-date catalog.

## Pricing

| Event | USD |
|-------|-----|
| Any audit / check_* tool call | $0.02 |
| `list_checks` discovery | $0.005 |

## Example response (truncated)

```json
{
  "summary": {
    "total_findings": 6,
    "by_severity": {"high": 2, "medium": 2, "low": 2, "info": 0}
  },
  "findings": [
    {
      "id": "DFA-021",
      "category": "security",
      "severity": "high",
      "instruction": "USER",
      "line_number": 3,
      "title": "USER root set explicitly",
      "description": "...",
      "remediation": "Switch to a non-root UID after any root-required RUN steps.",
      "fix_dockerfile_snippet": "USER 10001:10001",
      "references": ["CIS-Docker-4.1"]
    }
  ]
}
```

## Connecting from Claude Desktop

```json
{
  "mcpServers": {
    "dockerfile-audit": {
      "transport": "streamable-http",
      "url": "https://YOUR-ACTOR-URL.apify.actor/mcp"
    }
  }
}
```

## Limits

- **Dockerfile size:** 200 KB cap per audit
- **URL fetch:** 5s timeout, max 3 redirects, HTTPS only
- **Session timeout:** 5 minutes of inactivity

## What's NOT covered (yet)

- Live image vulnerability scanning (use Trivy / Grype for that)
- Multi-stage build optimization analysis (DFA-004 / DFA-005 — roadmapped)
- Compose-file audit (separate MCP: [`docker-compose-audit`](https://apify.com/unbearable_dev/docker-compose-audit))

## Sibling MCPs from Unbearable Labs

- **[`docker-compose-audit`](https://apify.com/unbearable_dev/docker-compose-audit)** — same pattern for `docker-compose.yml`
- **[`hu-postcode-validator`](https://apify.com/unbearable_dev/hu-postcode-validator)** — Hungarian postcode lookup

## Source / contact

Issues and ideas: `unbearabledev@gmail.com` or the GitHub org [`UnbearableDev`](https://github.com/UnbearableDev).
