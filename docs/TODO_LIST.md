# TODO List

## Phase 0 - Workspace Foundation

- [x] Choose project name: KyberM0nk.
- [x] Create documentation-first repository skeleton.
- [x] Create private GitHub repository under `m0nklabs`.
- [x] Push initial skeleton to GitHub.
- [x] Create local VS Code workspace file at `/home/flip/kyberm0nk.code-workspace`.
- [x] Add agent handoff prompt for the next workspace session.
- [ ] Open KyberM0nk in its own VS Code workspace.

## Phase 1 - Tool Discovery

- [ ] Add Guardian health-check script for host and Docker.
- [ ] Verify the current OpenCode install path and Docker support.
- [ ] Verify Aider configuration against Guardian `/v1`.
- [ ] Verify Agent Zero Docker deployment and mount strategy.
- [ ] Verify Continue local provider config format.

## Phase 2 - Docker Stack

- [ ] Add a minimal base image for shared agent tooling.
- [ ] Add a compose service for Aider.
- [ ] Add a compose service for OpenCode.
- [ ] Add a compose service for Agent Zero.
- [ ] Add shell wrappers under `scripts/`.

## Phase 3 - Safety and Observability

- [ ] Add mount validation before startup.
- [ ] Add Guardian health checks.
- [ ] Add per-tool logs with timestamps.
- [ ] Add a status command showing active project, reference mounts, and model target.
