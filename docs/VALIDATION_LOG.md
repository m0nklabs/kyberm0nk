# Validation Log

## 2026-05-10 - Release Hygiene Validation

Scope:

- Clean scratch experiments and raw probe data before publishing the Superset and Agent Zero work.
- Reconcile Superset documentation with the current Docker-sandbox wrapper path.
- Re-run focused syntax and build checks before committing.

Validation results:

| Check | Result | Notes |
|-------|--------|-------|
| MoniFuse backend syntax | Passed | `/home/linuxbrew/.linuxbrew/bin/python3 -m py_compile backend/llm_analysis.py` |
| MoniFuse frontend build | Passed | `npm run build` completed; Vite reported only the existing large chunk warning |
| Kyber shell syntax | Passed | `bash -n` passed for Superset wrappers, Agent Zero unstick, and project provisioning scripts |
| Kyber Python syntax | Passed | `/bin/python3 -m py_compile scripts/seed_superset_agents.py` |
| Kyber JSON configs | Passed | `jq empty` passed for changed Agent Zero model/project JSON configs |
| Whitespace checks | Passed | `git diff --check` passed for MoniFuse and KyberM0nk |

Operational note:

- `scripts/superset.sh` now documents and uses the sandbox Superset path: `/usr/local/superset/bin/superset` with state under `/root/.superset` in `kyberm0nk-sandbox-1`.

## 2026-05-09 - Agent Zero Loop Recovery

Scope:

- Stop Agent Zero from burning tokens in repeated missing-command thought loops.
- Reduce routine Agent Zero output/history budget and add explicit NewNexus anti-repeat recovery rules.
- Add a one-command unstick path for restarting the UI with tracked config reapplied.

Validation results:

| Check | Result | Notes |
|-------|--------|-------|
| Live log diagnosis | Passed | The running web log showed repeated thoughts around missing `windows-pwsh` and stale helper guidance |
| Source config update | Passed | `jq empty`, `bash -n`, `git diff --check`, and editor diagnostics passed after loop-safe config edits |
| Runtime restart | Passed | `scripts/agent_zero_unstick.sh` stopped the stuck UI process, reprovisioned NewNexus config, and restarted Agent Zero healthy on port `50001` |
| Effectiveness instruction update | Passed | Added state-delta and valid-but-useless action rules to Markdown and embedded project JSON, then verified the running sandbox contains both |
| GitHub credential dry-run logging | Passed | `provision_agent_zero_github.sh` now logs that the push check is dry-run only; remote `main` stayed at `d2ed89a54bd42a72d9c224945c523855e88e57f8` before and after provisioning |
| Stale quote-loop system guidance | Passed | Archived old Agent Zero chats with helper-based quote-loop guidance, force-recreated the sandbox so the file bind mount points at the clean patch inode, and verified active runtime code/chats no longer contain the blocker text |

Operational note:

- The first supervisor tick should detect repeated thoughts or repeated failed commands and emit `nudge` or `stop` before the model spends another full response on the same loop.

## 2026-05-09 - Superset Kyber Integration

Scope:

- Add Superset as the preferred Kyber session/worktree orchestration entry point.
- Add Guardian-backed OpenCode and Aider terminal-agent wrappers for Superset.
- Add an idempotent seeder for Kyber agent rows in the local Superset host database.

Validation results:

| Check | Result | Notes |
|-------|--------|-------|
| Shell syntax | Passed | `bash -n` passed for `scripts/superset.sh`, `scripts/superset-opencode-agent.sh`, and `scripts/superset-aider-agent.sh` |
| Python syntax | Passed | `py_compile` passed for `scripts/seed_superset_agents.py` |
| Superset binary resolution | Passed | Wrapper resolves the local evaluation CLI at `tmp/framework-evals/superset/packages/cli/dist/superset-linux-x64/bin/superset` |
| Link output | Passed | `scripts/superset.sh link` prints Superset website, docs, repository, CLI install link, and local state path |
| No-prompt guard | Passed | OpenCode and Aider wrappers exit with code `64` instead of blocking on interactive stdin |
| Seeder isolated DB smoke | Passed | Test host DB received `kyber-opencode` and `kyber-aider` rows |
| Superset OAuth login | Passed | `scripts/superset.sh login` authenticated the local CLI session for the active organization |
| Superset host distribution build | Passed | Built the Linux distribution bundle so `bin/superset` can start sibling `bin/superset-host` |
| Live Superset host status | Passed | `scripts/superset.sh start` launched a healthy local host daemon and `scripts/superset.sh status` reported healthy |
| Live agent seeding | Passed | `scripts/superset.sh seed-agents` inserted `kyber-opencode`, `kyber-aider`, and optional `kyber-claude-code` rows |
| Live project import | Passed | `scripts/superset.sh import-active` imported `/home/flip/kyberm0nk` through the local host-service tRPC API |
| Disposable workspace smoke | Passed | Created `kyber-superset-smoke` on branch `kyber/superset-smoke`; `git worktree list` shows the worktree under `~/.superset/worktrees/` |

Operational note:

- Live Superset host and workspace creation now work after OAuth login. The source-built CLI requires the full Linux distribution bundle, not only the standalone CLI binary, because `superset start` needs the sibling `superset-host` launcher.


## 2026-05-09 - Agent Zero 26B Default Restore

Scope:

- Stop Agent Zero from switching back to the slow Gemma4 31B uncensored profile by default.
- Keep the 31B profile available for explicit benchmarks and tuning only.

Validation results:

| Check | Result | Notes |
|-------|--------|-------|
| Live Guardian state before restore | Passed | Guardian was already loaded on `Huihui-gemma-4-26B-A4B-it-abliterated-Agent` and healthy |
| Source config validation | Passed | Global and NewNexus Agent Zero configs target `gemma4-26b-agent` for chat and utility models |
| Live Agent Zero config copy | Passed | Runtime `/opt/agent-zero/usr/plugins/_model_config/config.json` now reports `gemma4-26b-agent`, `4096`, `gemma4-26b-agent`, `2048` |
| `gemma4-agent` alias smoke | Passed with switch delay | Returned `GEMMA_AGENT_26B_OK`; request took about 75s because it had to switch away from the already-loaded 31B profile |
| Post-switch Guardian model | Partial | Guardian reported current model `Huihui-gemma-4-26B-A4B-it-abliterated-Agent`; backend health flag was still false immediately after the switch |
| Explicit 26B functional smoke | Blocked by active backend work | A follow-up `gemma4-26b-agent` request timed out after 120s while `llama-server` showed active GPU utilization, so the active AZ run was not interrupted |

Operational note:

- Do not remove the 31B profile; it may be smarter, but it is too slow for the default AZ loop until separately tuned.


## 2026-05-09 - Agent Zero Gemma4 31B Uncensored Correction

Scope:

- Correct Agent Zero away from the accidental Qwen32 max-agent route.
- Use the local Gemma4 31B uncensored model matching `TrevorJS/gemma-4-31B-it-uncensored`.
- Keep max reasoning enabled while preventing loops through source-edit guardrails.

Validation results:

| Check | Result | Notes |
|-------|--------|-------|
| Local model availability | Passed | `/home/flip/models/gemma-4-31B-it-uncensored-heretic-Q4_K_M.gguf` and `/home/flip/models/gemma-4-31B-it-mmproj-BF16.gguf` exist |
| Hugging Face source | Confirmed | `TrevorJS/gemma-4-31B-it-uncensored` is Gemma4, image-text-to-text, about 32.7B parameters, Apache-2.0 |
| Target Guardian alias | Passed | `gemma4-31b-uncensored-max-agent` returned `GEMMA31_OK` through Guardian `/v1/chat/completions` |
| Agent Zero runtime config | Passed | Running sandbox config reports `gemma4-31b-uncensored-max-agent` for chat and utility models |
| Windows source guard | Passed | `windows-pwsh` blocks source inspection through the Windows checkout with `WINDOWS_SOURCE_EDIT_BLOCKED` |
| Windows validation helper | Passed | `newnexus-windows-build status` runs successfully from the sandbox |

Operational note:

- This is not the earlier Gemma4 26B A4B compatibility profile and not the Qwen3-VL 32B route. It is the Gemma4 31B uncensored route the user requested.


## 2026-05-09 - Agent Zero Windows Source Edit Guard

Scope:

- Stop Agent Zero from repeatedly trying brittle PowerShell source edits against `J:\Unreal Projects\NewNexus`.
- Keep Windows available for pull/build/editor validation only.

Validation results:

| Check | Result | Notes |
|-------|--------|-------|
| Guard design | Ready for live validation | `windows-pwsh` blocks `Get-Content`, `Set-Content`, `Add-Content`, redirection, and Git write operations against the Windows NewNexus checkout |
| Dedicated build helper | Ready for live validation | Added `newnexus-windows-build status|pull|query-targets|build` to avoid hand-built PowerShell command strings |

Operational note:

- If Agent Zero needs to inspect or edit source, it must use `/a0/usr/projects/newnexus`. Windows is now only the Unreal validation executor.


## 2026-05-09 - Agent Zero NewNexus GitHub Push Plumbing

Scope:

- Let Agent Zero push NewNexus changes from the Linux sandbox instead of routing GitHub work through the Windows Unreal workstation.
- Keep GitHub tokens out of Git remotes, logs, and tracked files.

Validation results:

| Check | Result | Notes |
|-------|--------|-------|
| Deploy-key attempt | Blocked by GitHub policy | GitHub returned `Deploy keys are disabled for this repository` for `m0nklabs/NewNexus` |
| Credential helper design | Ready for live token | The sandbox reads `/run/kyberm0nk/secrets/github_token` through a Git credential helper instead of storing tokens in remotes |
| Full push smoke | Passed | Fresh token stored at `/home/flip/.secrets/kyberm0nk_github_token`; sandbox dry-run push returned `Everything up-to-date` |
| Stale credential cleanup | Passed | Removed the old `~/.secrets/github-tokens/` token files and the unused failed deploy-key files |

Operational note:

- Source work stays in `/a0/usr/projects/newnexus`. Agent Zero pushes from the sandbox, then the Windows checkout pulls the pushed commit before Unreal build/editor validation.


## 2026-05-09 - Windows Unreal .NET 8 Runtime

Scope:

- Resolve UnrealBuildTool failing on the Windows host because only .NET 9 was installed.
- Verify Agent Zero can continue through `windows-pwsh` after installing the required runtime.

Validation results:

| Check | Result | Notes |
|-------|--------|-------|
| Initial runtime inventory | Failed as expected | Windows had `Microsoft.NETCore.App 9.0.15` and `Microsoft.WindowsDesktop.App 9.0.15`, but no .NET 8 runtime |
| Runtime install | Passed | Installed `Microsoft.DotNet.Runtime.8` version `8.0.26` with `winget` |
| Runtime inventory after install | Passed | `dotnet --list-runtimes` now reports `Microsoft.NETCore.App 8.0.26` and `9.0.15` |
| UBT launch smoke | Passed | UBT no longer fails on missing .NET and wrote `J:\Unreal Projects\NewNexus\Intermediate\TargetInfo.json` |
| UBT build smoke | Reached next blocker | `NewNexusEditor Win64 Development` now reaches Unreal rules loading and fails on optional `VisualStudioTools` module rules |

Operational note:

- The next build blocker is not .NET. The project enables `VisualStudioTools` in `NewNexus.uproject`; UBT reports a `VisualStudioTools` module-rules error. Treat that plugin as optional IDE integration unless the user explicitly wants the Visual Studio plugin fixed instead of disabled.


## 2026-05-09 - Agent Zero Windows Helper Compatibility

Scope:

- Keep Agent Zero compatible with quote-loop guard guidance that tells it to use `windows-pwsh` and `windows-unreal-probe`.
- Avoid a Docker rebuild or sandbox recreation.
- Preserve the rule that source edits happen in `/a0/usr/projects/newnexus`, not directly through the Windows checkout.

Validation results:

| Check | Result | Notes |
|-------|--------|-------|
| Helper shell syntax | Passed | `bash -n` passed for `configs/agent-zero/bin/windows-pwsh`, `configs/agent-zero/bin/windows-unreal-probe`, and `scripts/provision_agent_zero_projects.sh` |
| Project JSON syntax | Passed | NewNexus `project.json` parses successfully after helper instruction updates |
| Helper provisioning | Passed | `scripts/provision_agent_zero_projects.sh --force` copied both helper commands into `/usr/local/bin/` in the running sandbox |
| PowerShell smoke | Passed | `windows-pwsh "Write-Output AZ_WINDOWS_PWSH_CLEAN"` returned clean output without CLIXML progress records or SSH known-host warnings |
| Unreal probe | Passed | `windows-unreal-probe` found `J:\UNREAL_ENGINE\UE_5.7` and the preferred `UnrealBuildTool.exe` path |

Operational note:

- The helpers are narrow wrappers for Windows discovery/build/run validation. They are not source-editing tools.
- The running Agent Zero chat may still contain older helper guidance; providing the helpers avoids turning that guidance into a dead end.


## 2026-05-09 - Tracked Agent Zero NewNexus Project

Scope:

- Track the Agent Zero `NewNexus` project metadata in the KyberM0nk repo so Docker rebuilds do not delete it permanently.
- Restore the project into the running sandbox without rebuilding or recreating the container.
- Point the Agent Zero project workspace at a persistent NewNexus checkout.

Validation results:

| Check | Result | Notes |
|-------|--------|-------|
| Shell syntax | Passed | `bash -n` passed for `ensure_newnexus_checkout.sh`, `provision_agent_zero_projects.sh`, `agent_zero_up.sh`, and existing provision/test scripts |
| Project JSON syntax | Passed | `project.json`, `agents.json`, and project model `config.json` parse successfully |
| Docker Compose config | Passed with warning | Compose config is valid; Compose still warns that top-level `version` is obsolete |
| Persistent checkout | Passed | `.agent-projects/NewNexus` exists as a normal clone of `m0nklabs/NewNexus` |
| Agent Zero project restore | Passed | `scripts/provision_agent_zero_projects.sh --force` restored `/opt/agent-zero/usr/projects/newnexus/.a0proj/project.json` |
| Agent Zero workspace path | Passed | `/a0/usr/projects/newnexus` is a symlink to `/workspace/project/.agent-projects/NewNexus` and contains `NewNexus.uproject` plus `.git` |
| Agent Zero health | Passed | `/api/health` returned successfully after provisioning |

Operational note:

- `scripts/agent_zero_up.sh` now restores tracked project templates on startup. Existing runtime projects are preserved unless `scripts/provision_agent_zero_projects.sh --force` is used.
- `.agent-projects/` is ignored by KyberM0nk because the game source belongs to the NewNexus repository, not this cockpit repository.
- Follow-up hardening removed stale runtime-only `windows-pwsh` / `windows-unreal-probe` binaries from the sandbox, configured Git `safe.directory` for `/workspace/project/.agent-projects/NewNexus`, and clarified that Agent Zero should edit `/a0/usr/projects/newnexus` while using Windows SSH only for build/run validation.
- Legacy note added 2026-05-25: the rows above document the old compatibility bridge. The current host-native path keeps the actual source repo at `~/NewNexus`, restores only Agent Zero project metadata under `~/agentzero/usr/projects/newnexus/.a0proj`, and no longer requires a NewNexus source symlink under `/a0/usr/projects/newnexus`.


## 2026-05-09 - Agent Zero Gemma4 Vision Route

Scope:

- Enable Agent Zero's Gemma4 chat route to advertise vision support.
- Keep Agent Zero on Guardian alias `gemma4-agent`, with Guardian carrying the Gemma4 multimodal projector.

Validation results:

| Check | Result | Notes |
|-------|--------|-------|
| Guardian direct vision smoke | Passed | `gemma4-agent` loaded with `--mmproj` and identified a generated red PNG as `red` |
| Agent Zero runtime config | Passed | `/opt/agent-zero/usr/plugins/_model_config/config.json` reports `chat_model.vision == true` |
| Agent Zero wrapper vision smoke | Passed | AZ `get_chat_model` / `LiteLLMChatWrapper` accepted a LangChain `HumanMessage` with `image_url` content and returned `red` |
| Windows executor regression smoke | Passed | `scripts/test_windows_unreal_ssh.sh` still reaches `14700K` from host and sandbox after the sandbox cleanup |
| Clipboard upload path smoke | Passed | `/a0/usr/uploads` now resolves to `/opt/agent-zero/usr/uploads`, where pasted clipboard images are stored |
| Clipboard image conversion smoke | Passed | A real pasted `/a0/usr/uploads/clipboard-*.png` file converted to a `data:image/png;base64,...` URL and produced a Gemma4 vision response through AZ's wrapper |

Operational note:

- `agent_zero_up.sh` previously used `docker compose up -d sandbox`, which allowed Compose to recreate the sandbox when service config drifted. It now starts an existing container directly and only creates a container with `--no-build` when none exists.
- Agent Zero's UI records pasted files as `/a0/usr/uploads/...`, while the container stores them under `/opt/agent-zero/usr/uploads/...`; the startup script now maintains a symlink for that path.
- Agent Zero's upstream `vision_load` passes local file paths as `image_url.url`; the Kyber patch converts those files to data URLs because Guardian/llama.cpp cannot read container-local paths from an OpenAI-compatible request.

## 2026-05-09 - Agent Zero Gemma4 Compatibility Smoke

Scope:

- Add Guardian alias `gemma4-agent` for a 65k-context Gemma4 26B A4B profile.
- Temporarily route Agent Zero chat and utility models to `gemma4-agent`.
- Verify direct Guardian inference, Agent Zero's LiteLLM wrapper, and the real Agent Zero UI/API message path.

Validation results:

| Check | Result | Notes |
|-------|--------|-------|
| Guardian YAML and AZ JSON syntax | Passed | Parsed `config/models.yaml` and `configs/agent-zero/model_config.json` successfully |
| Direct Guardian smoke | Passed | `gemma4-agent` returned `GEMMA4_OK` at about 40 tokens/sec decode |
| Agent Zero model-wrapper smoke | Passed | AZ LiteLLM route returned `AZ_GEMMA4_OK` |
| Agent Zero UI/API message smoke | Passed with observation | UI/API accepted a message and logged a `response` tool payload with `AZ_UI_GEMMA4_OK` |
| Whole-plan tool-loop observation | In progress | AZ created `/opt/agent-zero/usr/workdir/rimworld_sim/entities.py` through a subordinate/tool loop |
| GPU cleanup | Passed | Guardian `/admin/unload` stopped `llama-server`; only Frigate remained on GPU0 after cleanup |

Operational note:

- The UI/API message request exceeded a 20-second client timeout during first-run VectorDB/knowledge initialization, but Agent Zero continued and logged the correct response payload.
- Agent Zero logged `Memory consolidation timeout for area fragments` during the longer run, then continued and wrote the file. Treat this as AZ framework overhead to watch, not a Gemma4 inference failure.
- Keep the run bounded and monitor GPU status while deciding whether AZ is viable with Gemma4.

## 2026-05-08 - Balanced Local Agent Settings

Scope:

- Apply benchmark-based balanced model settings to OpenCode and Agent Zero.
- Document the server-wide policy in the shared MARK1/global Copilot config.
- Validate that both tools still route through Guardian and load the intended settings.

Validation results:

| Check | Result | Notes |
|-------|--------|-------|
| Agent Zero JSON syntax | Passed | `python3 -m json.tool configs/agent-zero/model_config.json` |
| Shell syntax | Passed | `bash -n scripts/opencode.sh scripts/agent_zero_up.sh scripts/agent_zero_down.sh` |
| Python helper syntax | Passed | `python3 -m py_compile scripts/benchmark_guardian_context.py scripts/render_benchmark_trends.py` |
| VS Code diagnostics | Passed | No errors for benchmark helper scripts or Agent Zero JSON |
| Docker Compose config | Passed with warning | Compose warns that top-level `version` is obsolete |
| OpenCode smoke test | Passed | Wrapper used `context=65536`, `max_tokens=4096`, `temperature=0.2`; model replied `KYBERM0NK_OPENCODE_OK` |
| Agent Zero startup | Passed | `/api/health` returned healthy JSON after restart |
| Agent Zero loaded config | Passed | Container config shows chat `65536/0.55/420s`, utility `32768/0.45/240s` |

Operational note:

- The long Qwen3.6 matrix benchmark was paused before final tool tests.
- Persisted benchmark rows remain in `logs/guardian-context-benchmarks/` and can be continued with `--resume`.
- A previous benchmark interruption left an orphaned `llama-server`; Guardian was reset before smoke tests.