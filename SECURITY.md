# Security Policy

## Reporting a Vulnerability

**Do not open a public GitHub issue for security-sensitive reports.**

Use GitHub's private vulnerability reporting instead:
https://github.com/militu/py-powens/security/advisories/new

Please include:

- A description of the issue and the potential impact.
- Steps to reproduce (ideally a minimal proof of concept).
- The SDK version affected.

Acknowledgement within 5 business days. A fix for confirmed vulnerabilities
is targeted within 30 days depending on severity.

## Scope

This policy covers the `py-powens` package itself.

**Out of scope**:

- Vulnerabilities in the Powens API (report to Powens directly).
- Vulnerabilities in transitive dependencies (`httpx`, `pydantic`) — report
  upstream; a dependency bump will ship once patched.

## Supported versions

Only the latest minor release line is patched for security.
