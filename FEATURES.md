# Feature Merge & Dedup — from 8 repos to 1 system

`pbo` (Personal | Business | CEO Operating System) is built by merging the **best
(non-duplicated) feature** for each task from eight cloned open-source repos. When two
or more repos offered the same capability, only the strongest was kept; the losers are
listed under "rejected duplicates".

## Sources (cloned into `_repos/`)

| Repo | What it contributes |
|---|---|
| `Volmarg/personal-management-system` (PMS) | Personal data entities: todos, contacts, calendar, goals, notes |
| `bradfeld/ceos` | EOS business machinery: V/TO, Rocks, Scorecard, L10, IDS, to-dos, cash-flow drivers |
| `starmynd-org/infinite-brain-os` | Git-backed markdown knowledge+work substrate (namespaces, validator) |
| `KOSASIH/aetherion-os` | 7-executive AI agent team + role-based `runAgent` + `executeGoal` god mode |
| `agems-ai/agems` | Agent org-chart / company-of-agents orchestration |
| `Orionfold Relay` | Client workspaces, human-approval gate, per-client cost roll-up |
| `OpenInsightHQ/openinsight` | Enterprise "AI employees", business-outcome framing |
| `ThinkInAIXYZ/deepchat` | Rich local-first agent client (skills/MCP/planning) — mined for feature ideas |

## Dedup decision table (feature → chosen repo → rejected duplicates)

| Task | Chosen | Rejected duplicates (why) |
|---|---|---|
| To-do / task tracking | **ceos-todos** (owner, deadline, completion rate) | PMS todolist (no owner/rate), aetherion Task kanban (on-chain focus) |
| Strategy / vision doc | **ceos-vto** (Vision/Traction) | infinite-brain knowledge (untyped), aetherion executeGoal (single-shot) |
| Quarterly priorities | **ceos-rocks** | aetherion Task board (no quarter/outcome), agems sprint (dev generic) |
| Weekly measurables | **ceos-scorecard** | infinite-brain metrics (no target/actual compare) |
| Structured meetings | **ceos-l10** + **ceos-ids** (issue resolution) | infinite-brain sessions (unstructured), relay meetings (agency ops) |
| Org / accountability | **ceos-accountability** (seats, owners, 5 roles) | agems agent org-chart (AI agents, not people) |
| Cash / treasury | **ceos-cashflow** (8 drivers) | aetherion on-chain SOL treasury (blockchain-specific) |
| Contacts | **PMS** | none of the others have a contact store |
| Calendar | **PMS** | none |
| Client / lead management | **built lean CRM** (client+deal pipeline+stages) | relay client-workspace (agency ops model), PMS (no deals), openinsight (enterprise) |
| Human approval gate | **relay** | openinsight (CI-style), aetherion (none) |
| Per-client cost roll-up | **relay** | aetherion treasury (crypto), PMS expenses (personal) |
| Agent team / role dispatch | **aetherion** (7→4 roles, runAgent, executeGoal) | agems (TypeScript heavy), openinsight (needs docker/mongo/meilisearch) |
| Knowledge substrate | **infinite-brain-os** (git-diffable markdown) | PMS (Vendor SQL), deepchat (Electron app), aetherion (Base44) |
| LLM reasoning engine | **deepchat** style skills/MCP mining | openinsight ONE-PI (commercial), agems (SaaS) |

## What was deliberately NOT merged (kept out)

- **deepchat**'s Electron desktop shell, 30-language i18n, and full MCP plugin tree — a
  client, not a system; only its agent/skill concepts were mined.
- **openinsight**'s docker/mongodb/meilisearch stack and commercial DMP engines — too
  heavy and partly commercial.
- **agems**'s Next.js/TypeScript platform + SaaS license — superseded by the lightweight
  aetherion-style role executor.
- **aetherion**'s Solana wallet/treasury — blockchain execution has no role here.
- **infinite-brain**'s Obsidian/VSCode-specific agents and n8n automations.

Net effect: pbo keeps the reasoning substrate (infinite-brain), the business machinery
(ceos), the personal layer (PMS), the deal/cost layer (relay), and the role-based agent
engine (aetherion) — one coherent, dependency-free, local-first tool.