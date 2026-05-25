# Roadmap & Vision: The Local Agentic Coding Cockpit

## The Core Hierarchy (Strategic to Operational)

The KyberM0nk stack maps directly to specific roles to form a cohesive, self-contained AI coding cockpit.

### 1. The Motor (Inference Backend)
- **Tool**: `llama.cpp` (GGUF) via Guardian.
- **Role**: The brain driving all other tools.
- **Setup**: Runs purely on the host (outside Docker). Configured to offload to GPU (`-ngl 99` for 35B models on 28GB VRAM). Uses the `qwen3-35b-uncensored` alias as the baseline.

### 2. The Primary Operator (Host-Native)
- **Tool**: Claude Code via the dedicated `claudecode` repo and `claude-local` launcher.
- **Role**: Main goto tool for high-trust coding work, architecture decisions, repo review, and orchestration entry.
- **Setup**: Runs purely on the host against Guardian. It is not part of the Docker sandbox.

### 3. The Secondary Local Generalist
- **Tool**: OpenCode.
- **Role**: Assists with broader local planning and routine throughput behind the main Claude lane.

### 4. The Executioner / Special Ops (Sandbox)
- **Tool**: Agent Zero.
- **Role**: Handles the dirty, system-level work. Stands parallel to OpenCode. Executes heavy scripts, complex installations, and environment debugging.
- **Safety**: Locked inside Docker with strictly mapped read-write targets and read-only reference mounts.

### 5. The Master Carpenter (Scalpel)
- **Tool**: Aider.
- **Role**: Extremely fast, precise code editor. Driven from the terminal while OpenCode sets the big picture. Highly token-efficient, performing surgical strikes on specific files.

### 6. The IDE-Glasses (Assistant)
- **Tool**: Continue (VS Code / JetBrains extension).
- **Role**: Direct line of sight into the code. Provides inline autocomplete and chat context. Does not perform massive autonomous structural changes, but accelerates manual typing and offers a window into the local proxy.

---

## Rollout Phases

### Phase 0 - Foundation (✅ DONE)
- [x] Clean repository and workspace creation.
- [x] Documentation skeleton, security rules, architectural boundaries.

### Phase 1, 2 & 3 - Setup & Observability (✅ DONE)
- [x] Guardian host & container health checks.
- [x] Dockerfile construction for Aider, OpenCode, and Agent Zero.
- [x] Shell wrappers with safety, mount validation, and ISO 8601 logging.

### Phase 4 - Aider Smoke-Test (The Scalpel First)
- Goal: Prove the "Master Carpenter" works flawlessly with Guardian.
- Deliverables: Send first prompt via Aider to edit a local file. Confirm token efficiency and editing workflow against the deep model.

### Phase 5 - OpenCode Orchestration (The General)
- Goal: Setup the autonomous planner.
- Deliverables: Configure OpenCode, verify planning capabilities, verify its capability to read the repo context and generate actionable sub-tasks.

### Phase 6 - Agent Zero Sandbox (Special Ops)
- Goal: Secure execution of complex tasks.
- Deliverables: Finalize strict mount mappings (read-write active, read-only reference), verify external script execution limitations, evaluate Docker socket safety.

### Phase 7 - Continue IDE Integration (The Glasses)
- Goal: Tie the proxy directly into VS Code.
- Deliverables: Set up `config.json` for Continue, hooking `autocomplete` and `chat` models strictly into the `127.0.0.1:11434/v1` Guardian proxy.

### Phase 8 - E2E Orchestration & Polish
- Goal: Seamless handoffs (e.g. OpenCode plans -> User guides Aider for quick edits -> Agent Zero runs the build).

### Phase 9 - Evidence-Based Model Tuning
- Goal: Keep local agents close to Copilot-style working patterns: broad available context, targeted retrieval, bounded output, and staged summaries.
- Deliverables:
	- Maintain Guardian context benchmark scripts and trend reports.
	- Use decision-order benchmarks for fast ballpark tuning before exhaustive matrices.
	- Keep OpenCode and Agent Zero defaults aligned with the latest stable benchmark evidence.
	- Avoid defaulting agent tools to maximum context plus maximum output unless an explicit deep benchmark or stress test requires it.

### Phase 10 - Supervisor Loop and Framework Reuse
- Goal: Reduce expensive cloud-agent usage by letting local agents do routine implementation work under a lightweight critic/supervisor loop.
- Direction:
	- Reuse an existing session/worktree orchestrator instead of rebuilding the cockpit from scratch.
	- Keep Claude Code as the main host-native operator lane, with its own tracked server setup under `~/claudecode/`.
	- Evaluate Claude Squad for the fast tmux/worktree TUI path.
	- Evaluate Superset for richer parallel-agent workspaces, review UI, and agent-agnostic orchestration.
	- Use OpenHands Software Agent SDK as a likely second worker path for programmable local coding loops; keep Agent Zero for sandbox/operator work until OpenHands remote workspace behavior is proven.
	- Keep Agent Zero as a sandbox/operator path, not the primary coding-agent default, unless future validation reverses the current evidence.
	- Use LangGraph supervisor patterns only if the local decision loop outgrows a simple structured script.
- Deliverables:
	- Keep `docs/SUPERVISOR_LOOP_PLAN.md` as the active design note.
	- Add a minimal supervisor tick that reads worker state, git state, validation state, and emits `continue`, `nudge`, `stop`, or `escalate`.
	- Reserve cloud review for repeated failures, risky diffs, architecture decisions, and pre-commit checkpoints.
