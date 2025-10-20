# Security Policy

## Supported versions
This is a personal hobby project. Security fixes are provided on a best‑effort basis for the latest commit and tagged releases; there is no SLA or guaranteed turnaround time.

DIY/personal use is free; commercial sales of preconfigured hardware or services require a commercial license (see `docs/legal/COMMERCIAL-LICENSE.md`).

## Reporting a vulnerability
- Please use GitHub to report privately:
	- Preferred: open a Security Advisory draft for this repository (GitHub > Security > Report a vulnerability) and include a clear description, reproduction steps, affected versions/tags, and any logs or PoCs.
	- If advisories are unavailable, open a new Issue with the "security" label and minimal details; I will migrate the discussion to a private channel.
- Avoid posting full details publicly until a fix is available.
- There is no guaranteed response time. I’ll review and respond as time permits and share remediation or mitigation details when available.

## Scope and notes
- This repository orchestrates third‑party services (OpenWrt, Jellyfin, etc.). Vulnerabilities in upstream components should be reported to their projects. If unsure, contact me and I can help triage on a best‑effort basis.
- No bug bounty program is offered.
