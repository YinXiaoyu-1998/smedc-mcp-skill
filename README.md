# SMEDC MCP Skill

Official installation and MCP usage guidance for employee-owned agents accessing SMEDC
(Small and Medium Enterprises Data Center). The approved package is
`smedc-mcp-launcher@0.13.1`, published and independently verified. Current installation authority
is [SKILL.md](skills/smedc-mcp/SKILL.md). [中文说明](README.zh.md).

## Scope And Documentation

The Skill covers official launcher installation, browser login, authorization-safe uploads/queries
and typed recovery. Employees enter passwords only in the official browser page; agents never
handle passwords, tokens or authorization codes. This repository does not operate service
infrastructure or execute business reports.

| Topic | Maintained entrypoint |
| --- | --- |
| Installation, client configuration, login and MCP tools | [Core Skill](skills/smedc-mcp/SKILL.md) |
| Skill replacement | [Update procedure](skills/smedc-mcp/references/update-skill.md) |
| Launcher upgrade and cleanup | [Upgrade procedure](skills/smedc-mcp/references/upgrade-cleanup.md) |
| Enterprise onboarding | [Admin UI entry](skills/smedc-mcp/references/tenant-onboarding.md) |
| Permissions and controlled management | [Business authorization](skills/smedc-mcp/references/business-authorization.md) |
| Cost-card directory and local CSV analysis | [Cost cards](skills/smedc-mcp/references/cost-cards.md) |
| Complete settled-order snapshots (future release gated) | [Settled orders](skills/smedc-mcp/references/settled-orders.md) |
| Platform review facts and identity | [Store reviews](skills/smedc-mcp/references/store-reviews.md) |
| Service-generated daily PDF archives | [Ledger tools](skills/smedc-mcp/references/ledger-pdf-tools.md) |
| DeepSeek Harness client configuration | [dsh wiring](skills/smedc-mcp/references/dsh-compat.md) |

Package publication, service deployment, tenant activation and client acceptance are separate.
Current service evidence belongs to the [service repository's readiness record](https://github.com/YinXiaoyu-1998/SME_DATA_CENTER/blob/main/docs/implementation/staging-readiness.md).
Do not maintain another live-version snapshot here or infer business access from package installation.

## Install The Skill

Retrieve [this repository](https://github.com/YinXiaoyu-1998/smedc-mcp-skill) and install only
`skills/smedc-mcp/`, using the [complete-directory replacement procedure](skills/smedc-mcp/references/update-skill.md).

| Platform | Canonical target |
| --- | --- |
| macOS/Linux | `~/.agents/skills/smedc-mcp` |
| Windows | `%USERPROFILE%\.agents\skills\smedc-mcp` |

Preserve local customizations and unrelated Skills. Keep recovery copies outside discovery roots;
do not overlay directories or leave `.bak` Skills there. Verify contents and the host's loaded copy;
a pending reload means activation is incomplete.

## Update The Skill

Ask the agent: “Update the smedc-mcp-skill skill.” Both `smedc-mcp` and `smedc-mcp-skill`
resolve to the latest default-branch `skills/smedc-mcp/` revision from
[YinXiaoyu-1998/smedc-mcp-skill](https://github.com/YinXiaoyu-1998/smedc-mcp-skill).
The [update procedure](skills/smedc-mcp/references/update-skill.md) owns retrieval, backup,
replacement, verification and cleanup. Report source commit, installation path and reload status.
A Skill-only update preserves the launcher and login session; a launcher upgrade needs its own
or a general SMEDC update request.

## Official Launcher

Use only `smedc-mcp-launcher@0.13.1`, with Node.js 22+ and npm. Never install npm `latest` or
use launcher self-update. The MCP entry is `smedc`, configured as local stdio with one `serve`
argument and `SMEDC_BASE_URL=https://api.smedatacenter.xyz`. Platform paths, exact commands,
self-check and host setup live in [Official Install Or Update](skills/smedc-mcp/SKILL.md#official-install-or-update).
macOS, Windows and Linux are supported; hosts without a secure store use memory-only sessions.
An upgrade follows the [complete upgrade procedure](skills/smedc-mcp/references/upgrade-cleanup.md);
self-check alone does not prove the host has reconnected to the new launcher.

## Optional Companions

[smedc-companion-skills](https://github.com/YinXiaoyu-1998/smedc-companion-skills) maintains
`smedc-business-analysis`, `smedc-delivery-ledger` and independent Meituan workflows. Install only
requested companions; a core install/update does not implicitly install or update them. Companions
use this core Skill's approved launcher pin while owning their business workflows.

## Maintenance

The complete `skills/smedc-mcp/` tree must match
[the service repository's copy](https://github.com/YinXiaoyu-1998/SME_DATA_CENTER/tree/main/skills/smedc-mcp)
byte-for-byte, including host-specific references. Change both in coordinated PRs. A Skill revision
is its Git commit, not a new launcher release. Documentation-only changes do not bump the launcher.

```bash
python3 -m unittest discover -s tests -v
```
