# Roadmap & Vision: The Local Agentic Coding Cockpit

## The Core Hierarchy (Strategic to Operational)

The KyberM0nk stack maps directly to specific roles to form a cohesive, self-contained AI coding cockpit.

### 1. The Motor (Inference Backend)
- **Tool**: `llama.cpp` (GGUF) via Guardian.
- **Role**: The brain driving all other tools.
- **Setup**: Runs purely on the host (outside Docker). Configured to offload to GPU (`-ngl 99` for 35B models on 28GB VRAM). Uses the `qwen3-35b-uncensored` alias as the baseline.

### 2. The General / Architect (Cockpit)
- **Tool**: OpenCode (or open-source Claude Code wrappers).
- **Role**: Strategic planning and autonomous orchestration. Sits "above" the rest. Understands the entire project scope, determines new architectures, and delegates chunks of work.

### 3. The Executioner / Special Ops (Sandbox)
- **Tool**: Agent Zero.
- **Role**: Handles the dirty, system-level work. Stands parallel to OpenCode. Executes heavy scripts, complex installations, and environment debugging.
- **Safety**: Locked inside Docker with strictly mapped read-write targets and read-only reference mounts.

### 4. The Master Carpenter (Scalpel)
- **Tool**: Aider.
- **Role**: Extremely fast, precise code editor. Driven from the terminal while OpenCode sets the big picture. Highly token-efficient, performing surgical strikes on specific files.

### 5. The IDE-Glasses (Assistant)
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
