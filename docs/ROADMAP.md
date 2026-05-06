# Roadmap

## Phase 0 - Foundation

Goal: create a clean repository and workspace for planning and implementation.

Deliverables:

- documentation skeleton
- private GitHub repository
- workspace file
- `.env.example`
- initial safety rules

## Phase 1 - Minimal Local Loop

Goal: prove one tool can talk to Guardian from a container.

Deliverables:

- Guardian health check script
- minimal Docker base image
- Aider container profile
- active project mount validation

## Phase 2 - Tool Stack

Goal: add the full local coding cockpit.

Deliverables:

- OpenCode runtime config
- Aider runtime config
- Agent Zero runtime config
- Continue config template
- scripts for launching each tool

## Phase 3 - Orchestration

Goal: make the tools pleasant to operate together.

Deliverables:

- status command
- active-project selector
- read-only reference mount generator
- per-tool log layout
- model target summary

## Phase 4 - Agent-Forge Reuse

Goal: bring over proven ideas from Agent-Forge without importing old complexity.

Candidates:

- role registry concepts
- monitoring dashboard ideas
- GitHub workflow automation patterns
- issue lifecycle rules
- log and health status patterns

## Phase 5 - Optional UI

Goal: add a thin local cockpit UI only if CLI wrappers are not enough.

Deliverables:

- local dashboard
- tool process status
- Guardian model status
- active project and mount visibility
