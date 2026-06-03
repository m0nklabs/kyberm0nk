# Testing Guide

How to validate that KyberM0nk components work correctly before and after changes.

## Quick Smoke Test

For a fast health check before pushing changes:

```bash
cd /home/flip/kyberm0nk
scripts/validate_docs.sh && scripts/test_quickstart.sh
echo "All checks passed"
```

**Pass criteria:** Both scripts exit `0`, no error output on stderr.

---

## Test Scripts

### `scripts/test_quickstart.sh`

**Purpose:** Verifies that the basic Kyber setup works end-to-end — validators pass, docs are in expected shape.

**How to run:**

```bash
cd /home/flip/kyberm0nk
scripts/test_quickstart.sh
```

**What it checks:**

- Documentation structure (docs/ directory, required files)
- Markdown link integrity
- `validate_kyber_tag_schema.py` passes
- `validate_docs.sh` passes

**Pass criteria:** Exit code `0`. Uses `set -euo pipefail`, so any failure stops immediately.

**Fail criteria:** Any validator fails or returns non-zero. Errors are written to stderr.

**Dependencies:** `bash`, `markdown-lint`, `validate_docs.sh`, `validate_kyber_tag_schema.py` (Python).

---

### `scripts/test_agent_zero_sandbox.sh`

**Purpose:** Validates that Agent Zero can launch inside a Docker sandbox with Kyber's wrapper.

**How to run:**

```bash
cd ~/.hermes/scripts
bash test_agent_zero_sandbox.sh
```

**What it checks:**

- Docker daemon reachable
- Sandbox image pulls successfully (if not cached)
- Agent Zero process starts inside container
- WebSocket endpoint responds (brief check)

**Pass criteria:** Exit code `0`, final line shows successful container exit.

**Fail criteria:** Container exit non-zero or fails to start. Note: this script **does not exit non-zero on failure** — check output for `"FAIL"` or `"ERROR"` strings.

**Dependencies:** Docker, Agent Zero installed in `~/.hermes/`.

---

### `scripts/test_aider_headless.sh`

**Purpose:** Smoke-tests Aider in headless mode via Guardian proxy — useful before queueing a real issue.

**How to run:**

```bash
cd ~/.hermes/scripts
bash test_aider_headless.sh
```

**What it checks:**

- Guardian proxy is up at `:11434`
- Aider binary is reachable (`$AIDER_BIN` or auto-detected)
- Aider sends one inference request through Guardian
- Response parses without error

**Pass criteria:** Exit code `0`, Aider prints a valid completion response.

**Fail criteria:** Guardian unreachable or Aider crashes mid-run. Note: errors are **not** propagated to exit code — check for `"FAIL"` or empty Aider output.

**Dependencies:** Guardian proxy running, Aider installed, `$AIDER_BIN` set or in `$PATH`.

---

### `scripts/test_az_ws.py`

**Purpose:** Tests WebSocket connectivity to a running Agent Zero instance.

**How to run:**

```bash
cd /home/flip/kyberm0nk
python3 ~/.hermes/scripts/test_az_ws.py
```

**What it checks:**

- Agent Zero web UI is reachable at configured host:port
- WebSocket handshake succeeds
- Sends a test chat message and receives response

**Pass criteria:** Exit code `0`, final message shows successful response.

**Fail criteria:** WebSocket handshake fails or message round-trip times out. **Bug: exceptions currently do not propagate — the script exits `0` even on failure.** Check output for `"Error"` or `"Timeout"` strings.

**Dependencies:** Agent Zero running (`agent-zero-web.service`), Python `websockets` library.

---

### `scripts/test_crewai_local.py`

**Purpose:** Validates that CrewAI can run a simple agent task against the local LLM via Guardian.

**How to run:**

```bash
cd ~/.hermes/venv/kyberm0nk  # if using venv
python3 ~/.hermes/scripts/test_crewai_local.py
```

**What it checks:**

- Guardian proxy responds to `/v1/models` — model is loadable
- CrewAI agent instantiates
- Simple task runs and produces non-empty output

**Pass criteria:** Exit code `0`, final task output is non-empty string.

**Fail criteria:** Guardian unreachable or CrewAI crashes. Errors are **not** propagated to exit code — check for `"Error"` or empty output.

**Dependencies:** Guardian proxy running, CrewAI installed in active Python env.

---

### `scripts/test_windows_unreal_ssh.sh`

**Purpose:** Verifies SSH connectivity to the Windows Unreal Engine host using Kyber's dedicated ed25519 key.

**How to run:**

```bash
bash ~/.hermes/scripts/test_windows_unreal_ssh.sh
```

**What it checks:**

- `~/.ssh/kyberm0nk_windows_unreal_ed25519` key file exists with correct permissions
- SSH connection to Windows host succeeds (using configured hostname/IP)
- Remote shell command runs and returns expected output

**Pass criteria:** Exit code `0`, output confirms remote execution.

**Fail criteria:** Key file missing, SSH connection refused, or remote command fails. Uses `set -euo pipefail` — failures exit non-zero immediately.

**Dependencies:** Windows host reachable on network, SSH configured.

---

## Validators

### `scripts/validate_docs.sh`

**Purpose:** Validates documentation integrity — presence of required files, markdown structure, internal links.

**How to run:**

```bash
cd /home/flip/kyberm0nk
scripts/validate_docs.sh
```

**What it checks:**

- Required files present: `README.md`, `CHANGELOG.md`, `docs/index.md`, `docs/ARCHITECTURE.md`, etc.
- `docs/index.json` has required keys (`version`, `docs`)
- Internal markdown links resolve
- Markdown passes basic lint rules

**Pass criteria:** Exit code `0`. Uses `set -euo pipefail`, so any failure stops immediately.

**Fail criteria:** Missing required file, broken link, or `index.json` invalid. Errors written to stderr with file:line where possible.

**Dependencies:** `bash`, `markdown-lint` (optional, for lint rules).

---

### `scripts/validate_kyber_tag_schema.py`

**Purpose:** Validates that code which posts or parses `kyber-tag:` comments on PRs conforms to the expected JSON schema.

**How to run:**

```bash
cd /home/flip/kyberm0nk
python3 scripts/validate_kyber_tag_schema.py
```

**What it checks:**

- `kyber-tag:` comment format: `kyber-tag: <type>` followed by optional JSON block
- Recognized tag types: `coding_subagent`, `ready_for_merge`, `rerun_reviewer`, `review_inconclusive`
- JSON payload, if present, parses with required fields

**Pass criteria:** Exit code `0`, no validation errors printed.

**Fail criteria:** Invalid tag type, malformed JSON, or missing required field. Errors written to stdout with script name and line.

**Dependencies:** Python 3, no external libraries.

---

## What Is Not Tested

- **Hermes queue integration** (end-to-end issue → PR → merge) — manual only, requires actual GitHub issue
- **OpenRouter tiered reviewer loop** — requires OpenRouter credits, only tested in production
- **Guardian inference quality** — Guardian owns that concern, Kyber only checks reachability
- **CrewAI multi-agent orchestration** — complex setup, tested in downstream repo

## Adding a New Test

When adding a new test script:

1. Place it in `scripts/` with a `test_` prefix
2. Use `set -euo pipefail` for Bash scripts — fail hard on first error
3. For Python tests, propagate exceptions to exit code (`sys.exit(1)` on failure)
4. Document it in this file under the appropriate section
5. Add it to `scripts/test_quickstart.sh` if it's a core health check

## See Also

- [OPERATOR_GUIDE.md](OPERATOR_GUIDE.md) — Production runtime procedures
- [ARCHITECTURE.md](ARCHITECTURE.md) — System structure for understanding test context
- [TODO_LIST.md](TODO_LIST.md) — Active work and follow-ups
