# SMEDC MCP Skill

The official runbook for employee-owned agents to install and use the SMEDC remote MCP
launcher. SMEDC stands for Small and Medium Enterprises Data Center. It uses browser login and
the official service origin `https://api.smedatacenter.xyz`; employees never give passwords,
tokens, or authorization codes to an agent.

This repository contains only skill and client-connection guidance. It never operates the SMEDC
API, database, vector store, storage, Docker, worker, cloud resources, or deployment.

> Live-service status: `smedc-mcp-launcher@0.5.1`, browser login, and the public HTTPS MCP
> boundary are the current packaging contract. Real employee login and backend authorization are
> still required. The launcher supports macOS, Windows, and Linux; headless Linux uses the same
> Device Authorization flow and falls back to a memory-only session when no secure store exists.

## Installation Profiles

### Core-only install

This is the default profile. Install only `smedc-mcp` for launcher setup, browser login, uploads,
and authorization-safe SMEDC queries. Optional companion skills are not required for ordinary SMEDC
work and are never installed silently by a core install or update.

### Optional companions

Both companions live in
[`YinXiaoyu-1998/smedc-companion-skills`](https://github.com/YinXiaoyu-1998/smedc-companion-skills)
and remain independently installed skills:

- `smedc-business-analysis` generates organization-backed operating diagnoses, weekly reports, and
  monthly reports.
- `smedc-delivery-ledger` renders the standard delivery-ledger table, exports the approved CSV, and
  guides receipt-linked quarantine-certificate photo operations.

If a companion is absent, an agent may identify the official source and offer to install it, but the
employee must explicitly authorize that installation or request the named companion or all
recommended companions. Installing or updating either repository does not update the other.

## Install The Skill

Clone or download this repository, then install the skill to the canonical current-user skill
directory. Do not default to `~/.codex/skills`.

| Platform         | Canonical target                         |
| ---------------- | ---------------------------------------- |
| macOS/Linux-like | `~/.agents/skills/smedc-mcp`             |
| Windows          | `%USERPROFILE%\.agents\skills\smedc-mcp` |

macOS/Linux-like shell:

```sh
mkdir -p "$HOME/.agents/skills"
SKILL_TARGET="$HOME/.agents/skills/smedc-mcp"
if [ -e "$SKILL_TARGET" ]; then
  mv "$SKILL_TARGET" "$SKILL_TARGET.bak.$(date +%Y%m%d%H%M%S)"
fi
cp -R skills/smedc-mcp "$SKILL_TARGET"
```

Windows PowerShell:

```powershell
$SkillRoot = Join-Path $env:USERPROFILE ".agents\skills"
$SkillTarget = Join-Path $SkillRoot "smedc-mcp"
New-Item -ItemType Directory -Force -Path $SkillRoot | Out-Null
if (Test-Path $SkillTarget) {
  Move-Item $SkillTarget "$SkillTarget.bak.$(Get-Date -Format yyyyMMddHHmmss)"
}
Copy-Item -Recurse "skills\smedc-mcp" $SkillTarget
```

Restart Codex or open a new task after installation so the skill list refreshes.

## Update The Skill

Ask your agent: "Update the smedc-mcp-skill skill." The installed skill recognizes both `smedc-mcp`
and `smedc-mcp-skill`, retrieves the latest default-branch revision from
[`YinXiaoyu-1998/smedc-mcp-skill`](https://github.com/YinXiaoyu-1998/smedc-mcp-skill), and backs up,
replaces, and verifies its complete skill directory. A marketplace listing is not required. The
agent reports the source commit and installation path; reload the host if needed.

Updating the skill alone preserves the launcher and login session. A launcher upgrade uses a
separate user request and the exact pin in the refreshed official skill. Network/write access and
the host's supported installation mechanism are still required. See the
[update procedure](skills/smedc-mcp/references/update-skill.md).

## Official Launcher

The only approved launcher package is `smedc-mcp-launcher@0.5.1`. Never use npm `latest`, an
unpinned version, or launcher self-update.

Run `node --version` and `npm --version` first. Node.js 22 or newer and a working npm are required.
An authorized employee-owned agent installs or repairs it idempotently:

```sh
npm install --prefix "<launcher-directory>" --save-exact smedc-mcp-launcher@0.5.1
```

Use the approved current-user launcher directory:

| Platform | Launcher directory                                                    |
| -------- | --------------------------------------------------------------------- |
| macOS    | `~/Library/Application Support/SMEDC/launcher/versions/0.5.1/`        |
| Windows  | `%LOCALAPPDATA%\\SMEDC\\launcher\\versions\\0.5.1\\`                  |
| Linux    | `${XDG_DATA_HOME:-$HOME/.local/share}/SMEDC/launcher/versions/0.5.1/` |

The agent must run the exact platform self-check before claiming success:

```sh
SMEDC_BASE_URL=https://api.smedatacenter.xyz \
  "$HOME/Library/Application Support/SMEDC/launcher/versions/0.5.1/node_modules/.bin/smedc-mcp-launcher" self-check
```

```powershell
$env:SMEDC_BASE_URL = "https://api.smedatacenter.xyz"
& "$env:LOCALAPPDATA\SMEDC\launcher\versions\0.5.1\node_modules\.bin\smedc-mcp-launcher.cmd" self-check
```

```sh
# Linux
SMEDC_LAUNCHER_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/SMEDC/launcher/versions/0.5.1"
SMEDC_BASE_URL=https://api.smedatacenter.xyz \
  "$SMEDC_LAUNCHER_DIR/node_modules/.bin/smedc-mcp-launcher" self-check
```

Self-check returns only safe machine-readable fields and never self-updates. An approved update
uses a new exact versioned directory, changes only the invoking agent's MCP launcher path, and
preserves any operating-system secure session. On Linux, `secureStore.available:false` is supported:
the launcher returns the first-party login link instead of opening a local browser when headless,
keeps the resulting session in memory only, and requires login again after launcher or host restart.

## Configuration And Login

Configure SMEDC as a local stdio launcher named `smedc`, not as a direct remote HTTP/OAuth server.
The complete launch tuple has one `serve` argument and one non-secret environment value:
`SMEDC_BASE_URL=https://api.smedatacenter.xyz`.

Before changing an MCP client, inspect its configuration and make a timestamped backup. Add or
replace only its `smedc` stdio entry; preserve every unrelated server and setting.

Use `smedc_auth_status` when authentication state is unknown. On `authentication_required`, invoke
`smedc_login` and ask the employee only to complete the browser page. After success, retry the
original business operation once. Use `smedc_logout` only on an employee's request.

When an employee asks which account is active, use the zero-input `smedc_get_current_user` tool. It
returns the authenticated employee's `displayName`, `email`, `role`, `clearance`, and
`organizationName`. The skill directory tool is `smedc_list_skills`.

## Contents

- `skills/smedc-mcp/SKILL.md`
- `skills/smedc-mcp/agents/openai.yaml`
- `skills/smedc-mcp/references/update-skill.md`
