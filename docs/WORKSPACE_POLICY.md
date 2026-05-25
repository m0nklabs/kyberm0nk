# Workspace Policy

Kyber treats agentic frameworks the same way VS Code treats a workspace: every framework should attach to one explicit project workspace instead of drifting across the home directory, hidden mirrors, or ad-hoc copies.

## Guiding Rule

- Every real project has one canonical source workspace, usually the Git checkout root such as `/home/flip/NewNexus`.
- Kyber itself is the control workspace, not a replacement for the source workspace of the project being edited.
- Each framework may keep its own metadata, session state, or project registration, but that state should resolve back to the same canonical source workspace.
- Hidden source mirrors, repo-local shadow copies, and broad home-directory default scopes are the wrong default. Use them only when a tool strictly requires them and document the exception.
- If a framework supports worktrees, sessions, or project registration, register the real source workspace or an explicit Git worktree for that project. Do not invent an ambiguous pseudo-workspace.

## Core Terms

- Control workspace: the Kyber repo and its VS Code workspace, used to coordinate frameworks and policy.
- Source workspace: the real project checkout that agents read and edit.
- Framework metadata: tool-owned state such as project manifests, sessions, caches, or prompts that can live outside the source workspace as long as they point back to it.
- Runtime root: an installed tool home or virtualenv location, not automatically the upstream source repo.

## Framework Mapping

### VS Code

VS Code uses a folder or `.code-workspace` file. This is the model Kyber follows conceptually: open one explicit project workspace instead of the whole home directory.

### Claude Code, Aider, and OpenCode

These tools should run with their current working directory or configured active project set to the canonical source workspace. Their logs or helper state may live elsewhere, but edit intent should still resolve to the same project root.

For Kyber's current host-native layout, Aider keeps its source checkout and runtime together under `~/aider`, OpenCode keeps its source checkout at `~/opencode` and its isolated worker runtime under `~/venvs/kyber-workers`, and both should still target the same explicit source workspace for any real task.

### Superset

Superset is the session and worktree cockpit. Its session, workspace, or imported project should still map to the same source workspace or to an explicit worktree created from that source workspace.

### CrewAI

Kyber keeps the upstream CrewAI source checkout at `~/crewAI` and the direct runtime at `~/crewai`. CrewAI should treat `project_path` as the canonical source workspace. Persisted controller state, status output, and live-run prompts should all agree on that same absolute path.

### Agent Zero

Agent Zero may keep project metadata under paths like `~/agentzero/usr/projects/<slug>/.a0proj`, but that metadata should describe and operate on the real source workspace such as `~/NewNexus`. Metadata storage is acceptable; source duplication is not the default.

## Practical Rules

- When adding a new framework integration, decide the canonical source workspace first.
- Make status commands show the same absolute source path the framework will edit.
- Keep framework-specific metadata outside the source tree when the tool benefits from it, but document the mapping clearly.
- Prefer one writable workspace per task. Extra repositories should be mounted or referenced read-only unless the operator intentionally opens another writable workspace.
- When handing work from one framework to another, preserve the same source workspace path in prompts, state files, and logs.

## Validation Checklist

Before calling a framework integration "workspace-ready," verify these:

- The framework reports a single explicit writable project path.
- That path is the real project checkout or an explicit Git worktree.
- Any helper metadata path is documented separately from the source workspace.
- Prompts, status output, and automation scripts all agree on the same source path.
- The integration does not silently depend on a hidden mirror or compatibility symlink.

## Current Kyber Examples

- Kyber control workspace: `/home/flip/kyberm0nk`
- NewNexus source workspace: `/home/flip/NewNexus`
- Aider host checkout + runtime: `/home/flip/aider`
- OpenCode host checkout: `/home/flip/opencode`
- Superset host checkout: `/home/flip/superset`
- CrewAI host checkout: `/home/flip/crewAI`
- CrewAI runtime root: `/home/flip/crewai`
- LangGraph host checkout: `/home/flip/langgraph`
- Agent Zero host checkout: `/home/flip/agentzero`
- Agent Zero NewNexus metadata: `/home/flip/agentzero/usr/projects/newnexus/.a0proj`

The rule of thumb is simple: one real project, one real source workspace, many framework-specific views of that same workspace.

See [WORKSPACE_INVENTORY.md](WORKSPACE_INVENTORY.md) for the current on-disk classification of each top-level workspace directory.