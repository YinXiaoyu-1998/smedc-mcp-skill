# SMEDC MCP Skill

面向员工自有智能体的企业资料中枢（Small and Medium Enterprises Data Center）安装与 MCP 使用指导。
已批准的包为 `smedc-mcp-launcher@0.13.1`，已公开发布并独立验证。
当前安装权威入口为 [SKILL.md](skills/smedc-mcp/SKILL.md)。[English](README.md)。

## 范围与文档

核心 Skill 负责官方 launcher 安装、浏览器登录、受权上传／查询和错误恢复。
员工只在官方浏览器页面输入密码，智能体不处理密码、token 或授权码。
本仓库不操作服务基础设施，也不执行业务报表。

| 主题 | 唯一维护入口 |
| --- | --- |
| 安装、客户端配置、登录与 MCP 工具 | [核心 Skill](skills/smedc-mcp/SKILL.md) |
| Skill 完整替换 | [更新流程](skills/smedc-mcp/references/update-skill.md) |
| Launcher 升级与清理 | [升级流程](skills/smedc-mcp/references/upgrade-cleanup.md) |
| 企业入驻 | [管理员 UI 入口](skills/smedc-mcp/references/tenant-onboarding.md) |
| 业务权限与受控管理 | [业务授权](skills/smedc-mcp/references/business-authorization.md) |
| 成本卡目录与本地 CSV 分析 | [成本卡](skills/smedc-mcp/references/cost-cards.md) |
| 平台评价事实与身份 | [门店评价](skills/smedc-mcp/references/store-reviews.md) |
| 服务端每日 PDF 台账 | [台账工具](skills/smedc-mcp/references/ledger-pdf-tools.md) |
| DeepSeek Harness 配置 | [dsh 接入](skills/smedc-mcp/references/dsh-compat.md) |

包发布、服务部署、租户激活和客户端验收分别取证。
服务状态统一见[服务仓库的核验记录](https://github.com/YinXiaoyu-1998/SME_DATA_CENTER/blob/main/docs/implementation/staging-readiness.md)，
这里不复制另一份线上版本快照，也不以安装成功推断业务授权。

## 安装 Skill

获取[本仓库](https://github.com/YinXiaoyu-1998/smedc-mcp-skill)，仅安装 `skills/smedc-mcp/`，
遵循[完整目录替换流程](skills/smedc-mcp/references/update-skill.md)。

| 平台 | Canonical 目录 |
| --- | --- |
| macOS/Linux | `~/.agents/skills/smedc-mcp` |
| Windows | `%USERPROFILE%\.agents\skills\smedc-mcp` |

保留本地定制和无关 Skills；恢复副本放在发现目录之外，不覆盖合并，也不在发现目录留下 `.bak`。
确认文件及宿主实际加载的新副本，需要重载时不得宣称已生效。

## 更新 Skill 本体

对 agent 说：“帮我更新 smedc-mcp-skill 这个 skill。”两个名称 `smedc-mcp` 和 `smedc-mcp-skill`
均指向 [YinXiaoyu-1998/smedc-mcp-skill](https://github.com/YinXiaoyu-1998/smedc-mcp-skill)
默认分支的最新 `skills/smedc-mcp/`。获取、备份、替换、验证和清理遵循[更新流程](skills/smedc-mcp/references/update-skill.md)。
完成后报告来源 commit、安装路径和重载状态。只更新 Skill 保留 launcher 与登录会话；
升级 launcher 需要单独的升级请求或一般 SMEDC 更新请求。

## 正式 Launcher

只使用 `smedc-mcp-launcher@0.13.1`，要求 Node.js 22+ 和 npm。
禁止安装 npm `latest` 或由 launcher 自更新。MCP entry 为 `smedc`，使用本地 stdio、
一个 `serve` 参数和 `SMEDC_BASE_URL=https://api.smedatacenter.xyz`。
平台路径、精确命令、自检和宿主配置统一见[安装流程](skills/smedc-mcp/SKILL.md#official-install-or-update)。
支持 macOS、Windows、Linux；没有安全存储时使用内存会话。
升级须完成[完整升级流程](skills/smedc-mcp/references/upgrade-cleanup.md)，单独自检不证明宿主已重连新版。

## 可选配套技能

[smedc-companion-skills](https://github.com/YinXiaoyu-1998/smedc-companion-skills)
维护 `smedc-business-analysis`、`smedc-delivery-ledger` 和独立美团工作流。
仅安装用户请求的 companion；核心安装／更新不隐含安装或更新配套技能。
Companion 使用核心 Skill 批准的 launcher pin，并各自维护业务流程。

## 维护

完整 `skills/smedc-mcp/` 必须与[服务仓库副本](https://github.com/YinXiaoyu-1998/SME_DATA_CENTER/tree/main/skills/smedc-mcp)
逐字节一致，包括宿主专用 reference；通过配套 PR 同步。Skill 修订以 Git commit 标识，
不等于 launcher 发布；纯文档修改不增加 launcher 版本。

```bash
python3 -m unittest discover -s tests -v
```
