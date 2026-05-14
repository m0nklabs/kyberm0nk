# Always-On Coding Monster Stack

## Goal

Build a multi-project, multi-agent coding cockpit where work keeps moving even when the operator is doing something else, while local models do the routine heavy lifting and premium/cloud agents are only used at high-value checkpoints.

## Hard Constraint

KyberM0nk currently has **one meaningful local coding-model lane** on the box.

That means the stack should optimize for:

- one active local LLM coding worker at a time
- multiple queued projects
- parallel non-LLM work around that one worker
- clean escalation when a stronger agent is actually worth spending

Trying to make several local coding agents reason in parallel on one box is the wrong optimization. The right optimization is a **serial LLM lease with parallel validation, browsing, Git, build, and review work** around it.

## Recommended Stack

### 1. Top-Level Orchestrator: Superset + Kyber Glue

Use **Superset** as the session/worktree/task orchestration layer.

Superset is **not** CrewAI.

- **Superset** = workspace/session/task control plane for coding agents
- **CrewAI** = agent-role/flow framework better suited for planning and delegation logic

Why:

- best current fit for multi-project workspaces and agent-session orchestration
- already validated in Kyber as the strongest cockpit candidate
- matches the need for a control plane above individual workers

Kyber should still own the environment-specific glue:

- Guardian routing
- project safety rules
- Windows Unreal boundaries
- local LLM lease scheduling
- review gates

### 2. Default Local Coding Workers: OpenCode + Aider

Use **OpenCode** as the general local worker and **Aider** as the focused editor.

Why:

- OpenCode is the best fit for planning, broader codebase reasoning, and interactive coding flow
- Aider remains the scalpel for tighter edit loops and smaller changes
- both can stay local through Guardian

This gives a simple worker split:

- OpenCode = planner/generalist/local senior
- Aider = surgical editor/local fixer

### 3. Secondary Programmable Worker: OpenHands SDK

Use **OpenHands SDK** as the programmable worker substrate for longer autonomous loops and structured runtime control.

Why:

- stronger programmable shape than Agent Zero for code-centric automation
- better fit for API-driven worker orchestration than a TUI-first tool
- good candidate for pinned workspace, iteration limit, and transcript-controlled local runs

OpenHands should complement Agent Zero first, not replace everything immediately.

### 4. Premium Escalation Layer: Claude Code / Claude Agent SDK

Use **Claude Code** as the premium benchmark and escalation agent.

Why:

- strongest coding-agent quality bar in the current stack
- already proven to work with Guardian, MCP, and project instruction layering
- best reserved for hard debugging, risky review, architecture-sensitive decisions, and final judgment

It should not be the default always-on worker when the whole point is to keep most routine work local.

### 5. Planning / PM Layer: CrewAI, Not Main Orchestrator

Use **CrewAI** for per-project planning, decomposition, and project-manager style coordination.

Do **not** use CrewAI as the main coding-orchestration substrate.

Why:

- strong for agent roles, crews, flows, and higher-level coordination
- weak fit for coding-specific worktree/session/diff management by itself
- better as the planning brain above workers, not the worker runtime itself

### 6. Supervisor Brain: Start Small, Upgrade to LangGraph Only If Needed

Start with a small Kyber `supervisor_tick` and only move to **LangGraph** if the state machine becomes too complex.

Why:

- LangGraph is strong for durable execution, state, and human-in-the-loop
- it is low-level orchestration infrastructure, not a ready-made coding cockpit
- using it too early would add framework weight before the actual control loop is proven

### 7. MCP Layer: Capability Registry as the Tool Catalog

The canonical MCP registry is [configs/mcp/servers.yaml](/home/flip/kyberm0nk/configs/mcp/servers.yaml).

Agents should request tools from that registry by capability.

Examples:

- ask for `github` tools when remote repo/issue/PR context is needed
- ask for `playwright` when browser validation is required
- ask for `vibeue` only for live Unreal work
- ask for `superset` when workspace/task/session orchestration is needed

## What Each Framework Is Best For

| Layer | Best Choice | Why |
|-------|-------------|-----|
| Multi-project control plane | Superset | Best fit for workspaces, tasks, sessions, and orchestration |
| Default local coding worker | OpenCode | Strongest local-first generalist role |
| Surgical local editing | Aider | Best focused edit loop |
| Programmable autonomous worker | OpenHands SDK | Strong API/runtime shape for controlled loops |
| Premium escalation | Claude Code | Highest coding-agent quality bar |
| Planning / PM | CrewAI | Good planner, wrong primary coding cockpit |
| Durable supervisor graph | LangGraph | Useful later if the supervisor becomes complex |

## Operating Model

### The serial local lane

Only one project at a time gets the local LLM lease.

Suggested queue fields:

- project id
- current branch/worktree
- task summary
- priority
- last progress timestamp
- failure count
- last validation result
- escalation state

### Parallel work that is still allowed

These do not need to block on the local model lane:

- test runs
- builds
- Git diff collection
- browser validation
- Unreal log collection
- static analysis
- repo indexing
- MCP-only environment discovery

### Escalation rules

Escalate to Claude Code or another premium agent only when:

- the same task fails twice
- the worker touches risky paths
- the architecture decision is unclear
- the change is ready for final review
- the local critic is not confident

## Why Not Pure Multi-Agent Parallelism

With one strong local inference lane, full parallel agent swarms mostly produce:

- scheduler contention
- VRAM churn
- lower-quality reasoning per active worker
- more context loss
- more heat and less real throughput

The better pattern is:

- one active local writer
- several queued projects
- cheap critics and validation around it
- premium agents only when they matter

## Immediate Build Direction

1. Keep Superset as the leading orchestration candidate.
2. Add a small Kyber scheduler that grants a single local LLM lease at a time.
3. Keep OpenCode and Aider as the default local workers behind that lease.
4. Add an OpenHands worker wrapper for longer programmable runs.
5. Keep Claude Code as escalation and review.
6. Use CrewAI for per-project PM/planning, not as the main coding runtime.
7. Require all tool requests to resolve through the MCP registry before new wrappers are invented.

## Non-Goal

KyberM0nk should **not** become a fresh generic agent framework.

It should become the local control surface that coordinates the best existing tools around:

- one serial local LLM lane
- multiple projects
- multiple worker types
- a strong MCP tool catalog
- disciplined escalation
