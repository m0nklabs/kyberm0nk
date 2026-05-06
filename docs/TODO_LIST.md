# TODO List

## Phase 0 - Workspace Foundation

- [x] Choose project name: KyberM0nk.
- [x] Create documentation-first repository skeleton.
- [x] Create private GitHub repository under `m0nklabs`.
- [x] Push initial skeleton to GitHub.
- [x] Create local VS Code workspace file at `/home/flip/kyberm0nk.code-workspace`.
- [x] Add agent handoff prompt for the next workspace session.
- [x] Open KyberM0nk in its own VS Code workspace.

## Phase 1 - Tool Discovery

- [x] Add Guardian health-check script for host and Docker.
- [x] Verify the current OpenCode install path and Docker support.
- [x] Verify Aider configuration against Guardian `/v1`.
- [x] Verify Agent Zero Docker deployment and mount strategy.
- [ ] Verify Continue local provider config format.

## Phase 2 - Docker Stack

- [x] Add a minimal base image for shared agent tooling. (Opted for separate tool images)
- [x] Add a compose service for Aider.
- [x] Add a compose service for OpenCode.
- [x] Add a compose service for Agent Zero.
- [x] Add shell wrappers under `scripts/`.

## Phase 3 - Safety and Observability

- [x] Add mount validation before startup.
- [x] Add Guardian health checks.
- [x] Add per-tool logs with timestamps.
- [x] Add a status command showing active project, reference mounts, and model target.

## Phase 4 - Aider Smoke Test (The Scalpel)

- [x] Execute `scripts/aider.sh` against the KyberM0nk repo itself.
- [x] Verify Aider can read the Guardian model via `host.docker.internal:11434/v1`.
- [x] Verify Aider can successfully apply a file edit (smoke test).
  - *Note: Proved volume mount & proxy work via shell commands, but Aider's parser struggles with Qwen3's diff generation. `whole` or `udiff` formats fail to apply automatically. Requires tuning `edit-format`.*
- [x] Confirm Aider logging output has proper timestamps in `logs/aider/`.

## Phase 5 - OpenCode Integration (The General)

- [x] Bootstrap OpenCode configuration inside its Docker context.
- [x] Verify it identifies the active project (`/workspace/project`).
- [x] Evaluate OpenCode's workspace context gathering capabilities.
- [x] Update `configs/opencode` with optimized system prompts for the General role.

## Phase 6 - Agent Zero Sandbox (Special Ops)

- [x] Verify Agent Zero strict mounts (rw on active, ro on references).
- [x] Run a test script via Agent Zero to confirm execution bounds.
- [x] Restrict Agent Zero from modifying parent/host resources unexpectedly (impl. via Docker `cap_drop` and `security_opt: no-new-privileges` in compose).

## Phase 7 - Continue IDE Integration (The Glasses)

- [ ] Generate standard `config.json` payload for Continue linking to Guardian.
- [ ] Place `config.json` in `configs/continue/` as a template for easy copying to `~/.continue/`.
- [ ] Verify autocomplete model routes to local endpoint.
