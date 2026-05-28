# Workspace Inventory

This file records what each current top-level workspace directory actually is on disk. The goal is to stop mixing up three different things:

- Git repository checkouts
- Runtime roots or virtualenv-only directories
- Local lab or scratch directories without a tracked upstream repo

The rule is simple: do not describe a path as a repository checkout unless a real `.git` directory exists there.

## Current Inventory

| Path | Kind | Git checkout | Notes |
|------|------|--------------|-------|
| `/home/flip/kyberm0nk` | Control repo | Yes | Main Kyber control plane repo. |
| `/home/flip/github-copilot-config` | Repo | Yes | Shared Copilot instruction/config repo. |
| `/home/flip/llama_cpp_guardian` | Repo | Yes | Guardian repo and active model-broker control surface. |
| `/home/flip/monifuse` | Repo | Yes | MoniFuse repo. |
| `/home/flip/superset` | Repo | Yes | Real Superset checkout. |
| `/home/flip/agentzero` | Repo | Yes | Real Agent Zero checkout plus runtime state under `runtime/` and `usr/`. |
| `/home/flip/hermes-agent` | Repo | Yes | Real Hermes-Agent checkout. |
| `/home/flip/aider` | Repo + runtime root | Yes | Real Aider checkout with the host runtime venv kept under `.venv/`. |
| `/home/flip/opencode` | Repo | Yes | Real OpenCode source checkout using the upstream repo name. |
| `/home/flip/crewAI` | Repo | Yes | Real CrewAI source checkout using the upstream repo name. |
| `/home/flip/langgraph` | Repo | Yes | Real LangGraph source checkout using the upstream repo name. |
| `/home/flip/claudecode` | Tracked config root | No | Host-tracked Claude Code files live here, but the current workspace copy is not a normal Git checkout. Treat it as a managed config tree unless/until a real repo checkout is present. |
| `/home/flip/.opencode` | Local install tree | No | Local OpenCode/OpenInterpreter install tree with package files and binaries, not a Git checkout. |
| `/home/flip/crewai` | Runtime root | No | Current direct CrewAI runtime virtualenv, not a CrewAI source repo checkout. |
| `/home/flip/langgraph-lab` | Local lab dir | No | Small local LangGraph experiment directory with no `.git` checkout in the current workspace copy. |

## How To Read This

- `Repo`: a normal project checkout with its own `.git` metadata.
- `Repo + runtime root`: a real Git checkout that also keeps the active tool runtime inside the same path.
- `Runtime root`: a directory primarily used to host an installed tool runtime or virtualenv.
- `Local install tree`: installed package files or binaries, but not the upstream source repo.
- `Local lab dir`: a local experiment folder that may have code, but is not currently a Git checkout.
- `Tracked config root`: managed configuration or launcher files that are important operationally, but are not currently a standard repo checkout.

## Policy

- When Kyber docs say `checkout`, that should mean a real Git checkout.
- When Kyber docs say `runtime root`, that should mean an installed tool environment or venv home.
- When Kyber docs say `source workspace`, that should mean the real project path being edited, such as `/home/flip/NewNexus`.
- If a framework only has a runtime root today, do not pretend the upstream tool repo already lives there.

## Current Practical Meaning

- `~/aider`, `~/superset`, `~/agentzero`, `~/hermes-agent`, `~/opencode`, `~/crewAI`, and `~/langgraph` are real repo checkouts.
- `~/aider` still doubles as a runtime root because its active `.venv` stays inside the checkout.
- `~/crewai` and `~/.opencode` are runtime/install trees, not source repos.
- `~/langgraph-lab` is currently just a local lab directory.
- `~/NewNexus` remains the canonical source workspace for the current game-development path. Editor session membership does not determine runtime ownership.