# Uitgebreide LLM Prijs/Kwaliteit Analyse (Live OpenRouter + LLM-Stats)

> **Tip:** Open `LLM_COST_PERFORMANCE_ANALYSIS.html` in je browser voor een **volledig interactief en sorteerbaar** overzicht!
> *Update data:* `python3 scripts/generate_llm_cost_analysis.py`

| Bedrijf | Model | Overall Rank (Arena) | Coding Rank | GPQA (Logic) Rank | Prompt (1M) | Completion (1M) | Context | Beschrijving |
|---|---|---|---|---|---|---|---|---|
| Qwen | `qwen/qwen3.5-35b-a3b` | #1 (17.1) | #86 (4.9) | #47 (84.2%) | $0.14 | $1.00 | 262144 | Qwen: Qwen3.5-35B-A3B |
| Nvidia | `nvidia/nemotron-3-super-120b-a12b:free` | #3 (14.9) | #122 (-0.6) | #56 (82.7%) | $0.00 | $0.00 | 262144 | NVIDIA: Nemotron 3 Super (free) |
| Nvidia | `nvidia/nemotron-3-super-120b-a12b` | #3 (14.9) | #122 (-0.6) | #56 (82.7%) | $0.09 | $0.45 | 262144 | NVIDIA: Nemotron 3 Super |
| Anthropic | `anthropic/claude-opus-4` | #4 (14.9) | #2 (20.1) | #9 (91.3%) | $15.00 | $75.00 | 200000 | Anthropic: Claude Opus 4 |
| Qwen | `qwen/qwen3.5-27b` | #5 (13.9) | #88 (4.8) | #40 (85.5%) | $0.20 | $1.56 | 262144 | Qwen: Qwen3.5-27B |
| X-ai | `x-ai/grok-4-fast` | #6 (13.6) | #75 (5.6) | - | $0.20 | $0.50 | 2000000 | xAI: Grok 4 Fast |
| Z-ai | `z-ai/glm-4.5-air:free` | #7 (13.4) | #58 (7.4) | #74 (79.1%) | $0.00 | $0.00 | 131072 | Z.ai: GLM 4.5 Air (free) |
| Z-ai | `z-ai/glm-4.5-air` | #7 (13.4) | #58 (7.4) | #74 (79.1%) | $0.13 | $0.85 | 131072 | Z.ai: GLM 4.5 Air |
| Z-ai | `z-ai/glm-4.5v` | #7 (13.4) | #58 (7.4) | #74 (79.1%) | $0.60 | $1.80 | 65536 | Z.ai: GLM 4.5V |
| Z-ai | `z-ai/glm-4.5` | #7 (13.4) | #58 (7.4) | #74 (79.1%) | $0.60 | $2.20 | 131072 | Z.ai: GLM 4.5 |
| Deepseek | `deepseek/deepseek-v3.2-exp` | #10 (13.0) | #57 (7.5) | #72 (79.9%) | $0.27 | $0.41 | 163840 | DeepSeek: DeepSeek V3.2 Exp |
| Qwen | `qwen/qwen3.5-122b-a10b` | #12 (12.8) | #63 (7.0) | #32 (86.6%) | $0.26 | $2.08 | 262144 | Qwen: Qwen3.5-122B-A10B |
| Google | `google/gemini-2.5-pro` | #13 (12.8) | #39 (9.3) | #53 (83.0%) | $1.25 | $10.00 | 1048576 | Google: Gemini 2.5 Pro |
| Google | `google/gemini-2.5-pro-preview` | #13 (12.8) | #39 (9.3) | #53 (83.0%) | $1.25 | $10.00 | 1048576 | Google: Gemini 2.5 Pro Preview 06-05 |
| Google | `google/gemini-2.5-pro-preview-05-06` | #13 (12.8) | #39 (9.3) | #53 (83.0%) | $1.25 | $10.00 | 1048576 | Google: Gemini 2.5 Pro Preview 05-06 |
| Openai | `openai/gpt-5-mini` | #14 (12.5) | #29 (10.9) | #59 (82.3%) | $0.25 | $2.00 | 400000 | OpenAI: GPT-5 Mini |
| Xiaomi | `xiaomi/mimo-v2-flash` | #18 (12.3) | #52 (7.9) | #50 (83.7%) | $0.10 | $0.30 | 262144 | Xiaomi: MiMo-V2-Flash |
| Google | `google/gemini-3.1-pro-preview-customtools` | #19 (12.2) | #1 (20.9) | #2 (94.3%) | $2.00 | $12.00 | 1048576 | Google: Gemini 3.1 Pro Preview Custom Tools |
| Google | `google/gemini-3.1-pro-preview` | #19 (12.2) | #1 (20.9) | #2 (94.3%) | $2.00 | $12.00 | 1048576 | Google: Gemini 3.1 Pro Preview |
| Moonshotai | `moonshotai/kimi-k2-thinking` | #21 (12.1) | #38 (9.4) | #45 (84.5%) | $0.60 | $2.50 | 262144 | MoonshotAI: Kimi K2 Thinking |
| X-ai | `x-ai/grok-4.1-fast` | #22 (12.0) | #87 (4.9) | #28 (87.5%) | $0.20 | $0.50 | 2000000 | xAI: Grok 4.1 Fast |
| X-ai | `x-ai/grok-4.3` | #22 (12.0) | #87 (4.9) | #28 (87.5%) | $1.25 | $2.50 | 1000000 | xAI: Grok 4.3 |
| Qwen | `qwen/qwen3-max-thinking` | #24 (11.8) | #65 (6.8) | #137 (62.0%) | $0.78 | $3.90 | 262144 | Qwen: Qwen3 Max Thinking |
| Qwen | `qwen/qwen3-max` | #24 (11.8) | #65 (6.8) | #137 (62.0%) | $0.78 | $3.90 | 262144 | Qwen: Qwen3 Max |
| Openai | `openai/gpt-4o` | #26 (11.7) | #94 (3.5) | #48 (84.0%) | $2.50 | $10.00 | 128000 | OpenAI: GPT-4o |
| Openai | `openai/gpt-5.2` | #27 (11.7) | #11 (15.1) | #7 (92.4%) | $1.75 | $14.00 | 400000 | OpenAI: GPT-5.2 |
| Z-ai | `z-ai/glm-5` | #28 (11.7) | #8 (15.8) | - | $0.60 | $1.92 | 202752 | Z.ai: GLM 5 |
| Z-ai | `z-ai/glm-5.1` | #28 (11.7) | #8 (15.8) | - | $1.05 | $3.50 | 202752 | Z.ai: GLM 5.1 |
| Z-ai | `z-ai/glm-5v-turbo` | #28 (11.7) | #8 (15.8) | - | $1.20 | $4.00 | 202752 | Z.ai: GLM 5V Turbo |
| Z-ai | `z-ai/glm-5-turbo` | #28 (11.7) | #8 (15.8) | - | $1.20 | $4.00 | 202752 | Z.ai: GLM 5 Turbo |
| Deepseek | `deepseek/deepseek-r1-0528` | #30 (11.5) | #92 (3.6) | #67 (81.0%) | $0.50 | $2.15 | 163840 | DeepSeek: R1 0528 |
| Deepseek | `deepseek/deepseek-r1` | #30 (11.5) | #92 (3.6) | #67 (81.0%) | $0.70 | $2.50 | 64000 | DeepSeek: R1 |
| Google | `google/gemini-3-flash-preview` | #31 (11.4) | #5 (16.9) | #11 (90.4%) | $0.50 | $3.00 | 1048576 | Google: Gemini 3 Flash Preview |
| Google | `google/gemini-2.5-flash-lite-preview-09-2025` | #32 (11.3) | #54 (7.8) | #54 (82.8%) | $0.10 | $0.40 | 1048576 | Google: Gemini 2.5 Flash Lite Preview 09-2025 |
| Google | `google/gemini-2.5-flash-lite` | #32 (11.3) | #54 (7.8) | #54 (82.8%) | $0.10 | $0.40 | 1048576 | Google: Gemini 2.5 Flash Lite |
| Google | `google/gemini-2.5-flash-image` | #32 (11.3) | #54 (7.8) | #54 (82.8%) | $0.30 | $2.50 | 32768 | Google: Nano Banana (Gemini 2.5 Flash Image) |
| Google | `google/gemini-2.5-flash` | #32 (11.3) | #54 (7.8) | #54 (82.8%) | $0.30 | $2.50 | 1048576 | Google: Gemini 2.5 Flash |
| Minimax | `minimax/minimax-m2.5:free` | #34 (11.2) | #36 (9.6) | - | $0.00 | $0.00 | 196608 | MiniMax: MiniMax M2.5 (free) |
| Minimax | `minimax/minimax-m2` | #34 (11.2) | #36 (9.6) | - | $0.26 | $1.00 | 196608 | MiniMax: MiniMax M2 |
| Minimax | `minimax/minimax-m2.5` | #34 (11.2) | #36 (9.6) | - | $0.15 | $1.15 | 196608 | MiniMax: MiniMax M2.5 |
| Openai | `openai/gpt-5.4-nano` | #35 (11.0) | #4 (17.3) | #6 (92.8%) | $0.20 | $1.25 | 400000 | OpenAI: GPT-5.4 Nano |
| Openai | `openai/gpt-5.4-mini` | #35 (11.0) | #4 (17.3) | #6 (92.8%) | $0.75 | $4.50 | 400000 | OpenAI: GPT-5.4 Mini |
| Openai | `openai/gpt-5` | #35 (11.0) | #4 (17.3) | #6 (92.8%) | $1.25 | $10.00 | 400000 | OpenAI: GPT-5 |
| Openai | `openai/gpt-5.4-image-2` | #35 (11.0) | #4 (17.3) | #6 (92.8%) | $8.00 | $15.00 | 272000 | OpenAI: GPT-5.4 Image 2 |
| Openai | `openai/gpt-5.4` | #35 (11.0) | #4 (17.3) | #6 (92.8%) | $2.50 | $15.00 | 1050000 | OpenAI: GPT-5.4 |
| Openai | `openai/gpt-5.4-pro` | #35 (11.0) | #4 (17.3) | #6 (92.8%) | $30.00 | $180.00 | 1050000 | OpenAI: GPT-5.4 Pro |
| Baidu | `baidu/ernie-4.5-21b-a3b-thinking` | #37 (11.0) | #110 (1.2) | #96 (74.0%) | $0.07 | $0.28 | 131072 | Baidu: ERNIE 4.5 21B A3B Thinking |
| Baidu | `baidu/ernie-4.5-21b-a3b` | #37 (11.0) | #110 (1.2) | #96 (74.0%) | $0.07 | $0.28 | 120000 | Baidu: ERNIE 4.5 21B A3B |
| Baidu | `baidu/ernie-4.5-vl-28b-a3b` | #37 (11.0) | #110 (1.2) | #96 (74.0%) | $0.14 | $0.56 | 30000 | Baidu: ERNIE 4.5 VL 28B A3B |
| Baidu | `baidu/ernie-4.5-300b-a47b` | #37 (11.0) | #110 (1.2) | #96 (74.0%) | $0.28 | $1.10 | 123000 | Baidu: ERNIE 4.5 300B A47B  |
| Baidu | `baidu/ernie-4.5-vl-424b-a47b` | #37 (11.0) | #110 (1.2) | #96 (74.0%) | $0.42 | $1.25 | 123000 | Baidu: ERNIE 4.5 VL 424B A47B  |
| Openai | `openai/gpt-5.1-codex` | #38 (10.9) | #59 (7.2) | - | $1.25 | $10.00 | 400000 | OpenAI: GPT-5.1-Codex |
| Mistralai | `mistralai/mistral-large` | #42 (10.8) | #69 (6.4) | #173 (43.9%) | $2.00 | $6.00 | 128000 | Mistral Large |
| Z-ai | `z-ai/glm-4.6v` | #43 (10.8) | #24 (11.4) | #65 (81.0%) | $0.30 | $0.90 | 131072 | Z.ai: GLM 4.6V |
| Z-ai | `z-ai/glm-4.6` | #43 (10.8) | #24 (11.4) | #65 (81.0%) | $0.39 | $1.90 | 204800 | Z.ai: GLM 4.6 |
| Deepseek | `deepseek/deepseek-v3.2` | #44 (10.7) | #48 (8.3) | - | $0.25 | $0.38 | 131072 | DeepSeek: DeepSeek V3.2 |
| Deepseek | `deepseek/deepseek-v3.2-speciale` | #44 (10.7) | #48 (8.3) | - | $0.29 | $0.43 | 163840 | DeepSeek: DeepSeek V3.2 Speciale |
| Minimax | `minimax/minimax-m2.1` | #45 (10.7) | #41 (9.1) | #66 (81.0%) | $0.29 | $0.95 | 196608 | MiniMax: MiniMax M2.1 |
| Moonshotai | `moonshotai/kimi-k2-0905` | #47 (10.5) | #33 (10.0) | #84 (75.8%) | $0.40 | $2.00 | 262144 | MoonshotAI: Kimi K2 0905 |
| Stepfun | `stepfun/step-3.5-flash` | #48 (10.5) | #71 (5.9) | - | $0.10 | $0.30 | 262144 | StepFun: Step 3.5 Flash |
| X-ai | `x-ai/grok-code-fast-1` | #50 (10.4) | #89 (4.6) | - | $0.20 | $1.50 | 256000 | xAI: Grok Code Fast 1 |
| Qwen | `qwen/qwen3-coder:free` | #51 (10.3) | #72 (5.9) | - | $0.00 | $0.00 | 262000 | Qwen: Qwen3 Coder 480B A35B (free) |
| Qwen | `qwen/qwen3-coder-30b-a3b-instruct` | #51 (10.3) | #72 (5.9) | - | $0.07 | $0.27 | 160000 | Qwen: Qwen3 Coder 30B A3B Instruct |
| Qwen | `qwen/qwen3-coder-next` | #51 (10.3) | #72 (5.9) | - | $0.11 | $0.80 | 262144 | Qwen: Qwen3 Coder Next |
| Qwen | `qwen/qwen3-coder-flash` | #51 (10.3) | #72 (5.9) | - | $0.20 | $0.97 | 1000000 | Qwen: Qwen3 Coder Flash |
| Qwen | `qwen/qwen3-coder` | #51 (10.3) | #72 (5.9) | - | $0.22 | $1.80 | 262144 | Qwen: Qwen3 Coder 480B A35B |
| Qwen | `qwen/qwen3-coder-plus` | #51 (10.3) | #72 (5.9) | - | $0.65 | $3.25 | 1000000 | Qwen: Qwen3 Coder Plus |
| Openai | `openai/gpt-5.1` | #53 (10.2) | #19 (12.3) | #19 (88.1%) | $1.25 | $10.00 | 400000 | OpenAI: GPT-5.1 |
| Z-ai | `z-ai/glm-4.7-flash` | #54 (10.2) | #31 (10.7) | #36 (85.7%) | $0.06 | $0.40 | 202752 | Z.ai: GLM 4.7 Flash |
| Z-ai | `z-ai/glm-4.7` | #54 (10.2) | #31 (10.7) | #36 (85.7%) | $0.40 | $1.75 | 202752 | Z.ai: GLM 4.7 |
| Moonshotai | `moonshotai/kimi-k2.5` | #57 (10.0) | #12 (14.6) | #27 (87.6%) | $0.44 | $2.00 | 262144 | MoonshotAI: Kimi K2.5 |
| Moonshotai | `moonshotai/kimi-k2` | #57 (10.0) | #12 (14.6) | #27 (87.6%) | $0.57 | $2.30 | 131072 | MoonshotAI: Kimi K2 0711 |
| Qwen | `qwen/qwen3-30b-a3b-instruct-2507` | #58 (10.0) | #100 (2.4) | #126 (65.8%) | $0.09 | $0.30 | 262144 | Qwen: Qwen3 30B A3B Instruct 2507 |
| Qwen | `qwen/qwen3-30b-a3b-thinking-2507` | #58 (10.0) | #100 (2.4) | #126 (65.8%) | $0.08 | $0.40 | 131072 | Qwen: Qwen3 30B A3B Thinking 2507 |
| Qwen | `qwen/qwen3-30b-a3b` | #58 (10.0) | #100 (2.4) | #126 (65.8%) | $0.09 | $0.45 | 40960 | Qwen: Qwen3 30B A3B |
| Minimax | `minimax/minimax-m2.7` | #59 (10.0) | #47 (8.3) | #77 (78.0%) | $0.30 | $1.20 | 196608 | MiniMax: MiniMax M2.7 |
| Minimax | `minimax/minimax-m2-her` | #59 (10.0) | #47 (8.3) | #77 (78.0%) | $0.30 | $1.20 | 65536 | MiniMax: MiniMax M2-her |
| Openai | `openai/gpt-oss-120b` | #61 (9.9) | #81 (5.4) | #69 (80.9%) | $0.04 | $0.18 | 131072 | OpenAI: gpt-oss-120b |
| Openai | `openai/gpt-oss-120b:free` | #62 (9.9) | #96 (3.3) | #71 (80.1%) | $0.00 | $0.00 | 131072 | OpenAI: gpt-oss-120b (free) |
| Xiaomi | `xiaomi/mimo-v2-pro` | #63 (9.8) | #102 (2.2) | - | $1.00 | $3.00 | 1048576 | Xiaomi: MiMo-V2-Pro |
| Qwen | `qwen/qwen3.5-397b-a17b` | #64 (9.6) | #20 (12.1) | #17 (88.4%) | $0.39 | $2.34 | 262144 | Qwen: Qwen3.5 397B A17B |
| Deepseek | `deepseek/deepseek-chat-v3.1` | #66 (9.6) | #62 (7.0) | - | $0.15 | $0.75 | 32768 | DeepSeek: DeepSeek V3.1 |
| Deepseek | `deepseek/deepseek-chat-v3-0324` | #66 (9.6) | #62 (7.0) | - | $0.20 | $0.77 | 163840 | DeepSeek: DeepSeek V3 0324 |
| Deepseek | `deepseek/deepseek-chat` | #66 (9.6) | #62 (7.0) | - | $0.32 | $0.89 | 163840 | DeepSeek: DeepSeek V3 |
| Anthropic | `anthropic/claude-sonnet-4` | #67 (9.6) | #13 (14.2) | #14 (89.9%) | $3.00 | $15.00 | 1000000 | Anthropic: Claude Sonnet 4 |
| Nvidia | `nvidia/nemotron-3-nano-30b-a3b:free` | #68 (9.5) | #107 (1.9) | #89 (75.0%) | $0.00 | $0.00 | 256000 | NVIDIA: Nemotron 3 Nano 30B A3B (free) |
| Nvidia | `nvidia/nemotron-3-nano-30b-a3b` | #68 (9.5) | #107 (1.9) | #89 (75.0%) | $0.05 | $0.20 | 262144 | NVIDIA: Nemotron 3 Nano 30B A3B |
| Qwen | `qwen/qwen3-235b-a22b-thinking-2507` | #69 (9.4) | #93 (3.6) | #64 (81.1%) | $0.15 | $1.50 | 131072 | Qwen: Qwen3 235B A22B Thinking 2507 |
| Qwen | `qwen/qwen3-235b-a22b` | #69 (9.4) | #93 (3.6) | #64 (81.1%) | $0.45 | $1.82 | 131072 | Qwen: Qwen3 235B A22B |
| X-ai | `x-ai/grok-4.20` | #75 (9.0) | #34 (9.9) | - | $1.25 | $2.50 | 2000000 | xAI: Grok 4.20 |
| X-ai | `x-ai/grok-4` | #75 (9.0) | #34 (9.9) | - | $3.00 | $15.00 | 256000 | xAI: Grok 4 |
| Google | `google/gemma-4-31b-it:free` | #79 (8.8) | #35 (9.8) | #46 (84.3%) | $0.00 | $0.00 | 262144 | Google: Gemma 4 31B (free) |
| Google | `google/gemma-4-31b-it` | #79 (8.8) | #35 (9.8) | #46 (84.3%) | $0.13 | $0.38 | 262144 | Google: Gemma 4 31B |
| Openai | `openai/gpt-5.5` | #83 (8.2) | #7 (15.8) | #4 (93.6%) | $5.00 | $30.00 | 1050000 | OpenAI: GPT-5.5 |
| Openai | `openai/gpt-5.5-pro` | #83 (8.2) | #7 (15.8) | #4 (93.6%) | $30.00 | $180.00 | 1050000 | OpenAI: GPT-5.5 Pro |
| Openai | `openai/gpt-5.3-codex` | #84 (8.2) | #18 (12.4) | - | $1.75 | $14.00 | 400000 | OpenAI: GPT-5.3-Codex |
| Openai | `openai/gpt-5.2-codex` | #85 (8.1) | #23 (11.6) | - | $1.75 | $14.00 | 400000 | OpenAI: GPT-5.2-Codex |
| Openai | `openai/gpt-5.1-codex-mini` | #86 (8.1) | #61 (7.1) | - | $0.25 | $2.00 | 400000 | OpenAI: GPT-5.1-Codex-Mini |
| Openai | `openai/gpt-5.1-codex-max` | #86 (8.1) | #61 (7.1) | - | $1.25 | $10.00 | 400000 | OpenAI: GPT-5.1-Codex-Max |
| Google | `google/gemini-3.1-flash-lite` | #88 (7.6) | #22 (11.6) | #31 (86.9%) | $0.25 | $1.50 | 1048576 | Google: Gemini 3.1 Flash Lite |
| Google | `google/gemini-3.1-flash-lite-preview` | #88 (7.6) | #22 (11.6) | #31 (86.9%) | $0.25 | $1.50 | 1048576 | Google: Gemini 3.1 Flash Lite Preview |
| Qwen | `qwen/qwen3.6-plus` | #89 (7.5) | #14 (13.5) | #12 (90.4%) | $0.33 | $1.95 | 1000000 | Qwen: Qwen3.6 Plus |
| Qwen | `qwen/qwen3-32b` | #90 (7.4) | #97 (3.1) | - | $0.08 | $0.28 | 40960 | Qwen: Qwen3 32B |
| X-ai | `x-ai/grok-4.20-multi-agent` | #92 (7.0) | #68 (6.6) | - | $2.00 | $6.00 | 2000000 | xAI: Grok 4.20 Multi-Agent |
| Openai | `openai/gpt-5.3-chat` | #93 (7.0) | #77 (5.5) | - | $1.75 | $14.00 | 128000 | OpenAI: GPT-5.3 Chat |
| Deepseek | `deepseek/deepseek-v4-flash` | #95 (6.3) | #46 (8.5) | #23 (88.1%) | $0.14 | $0.28 | 1048576 | DeepSeek: DeepSeek V4 Flash |
| Google | `google/gemma-4-26b-a4b-it:free` | #96 (5.9) | #30 (10.7) | #60 (82.3%) | $0.00 | $0.00 | 262144 | Google: Gemma 4 26B A4B  (free) |
| Google | `google/gemma-4-26b-a4b-it` | #96 (5.9) | #30 (10.7) | #60 (82.3%) | $0.06 | $0.33 | 262144 | Google: Gemma 4 26B A4B  |
| Openai | `openai/gpt-oss-20b:free` | #97 (5.9) | #78 (5.5) | #103 (71.5%) | $0.00 | $0.00 | 131072 | OpenAI: gpt-oss-20b (free) |
| Openai | `openai/gpt-oss-20b` | #97 (5.9) | #78 (5.5) | #103 (71.5%) | $0.03 | $0.14 | 131072 | OpenAI: gpt-oss-20b |
| Openai | `openai/gpt-4.1-mini` | #99 (5.3) | #37 (9.5) | #131 (65.0%) | $0.40 | $1.60 | 1047576 | OpenAI: GPT-4.1 Mini |
| Openai | `openai/gpt-4.1` | #99 (5.3) | #37 (9.5) | #131 (65.0%) | $2.00 | $8.00 | 1047576 | OpenAI: GPT-4.1 |
| Openai | `openai/gpt-4` | #99 (5.3) | #37 (9.5) | #131 (65.0%) | $30.00 | $60.00 | 8191 | OpenAI: GPT-4 |
| Deepseek | `deepseek/deepseek-v4-pro` | #100 (5.1) | #28 (11.0) | #13 (90.1%) | $0.43 | $0.87 | 1048576 | DeepSeek: DeepSeek V4 Pro |
| Openai | `openai/gpt-5-nano` | #101 (5.1) | #67 (6.6) | #104 (71.2%) | $0.05 | $0.40 | 400000 | OpenAI: GPT-5 Nano |
| Xiaomi | `xiaomi/mimo-v2-omni` | #103 (4.4) | #106 (1.9) | - | $0.40 | $2.00 | 262144 | Xiaomi: MiMo-V2-Omni |
| Inception | `inception/mercury-2` | #106 (3.2) | #103 (2.1) | #95 (74.0%) | $0.25 | $0.75 | 128000 | Inception: Mercury 2 |
| Qwen | `qwen/qwen3.6-27b` | #107 (2.7) | #85 (5.0) | #26 (87.8%) | $0.32 | $3.20 | 262144 | Qwen: Qwen3.6 27B |
| Moonshotai | `moonshotai/kimi-k2.6` | #109 (-3.9) | #17 (12.5) | #10 (90.5%) | $0.75 | $3.50 | 262144 | MoonshotAI: Kimi K2.6 |
| Openrouter | `openrouter/pareto-code` | - | - | - | $-1000000.00 | $-1000000.00 | 2000000 | Pareto Code Router |
| Openrouter | `openrouter/bodybuilder` | - | - | - | $-1000000.00 | $-1000000.00 | 128000 | Body Builder (beta) |
| Openrouter | `openrouter/auto` | - | - | - | $-1000000.00 | $-1000000.00 | 2000000 | Auto Router |
| Inclusionai | `inclusionai/ring-2.6-1t:free` | - | - | - | $0.00 | $0.00 | 262144 | inclusionAI: Ring-2.6-1T (free) |
| Baidu | `baidu/cobuddy:free` | - | - | - | $0.00 | $0.00 | 131072 | Baidu Qianfan: CoBuddy (free) |
| Openrouter | `openrouter/owl-alpha` | - | - | - | $0.00 | $0.00 | 1048756 | Owl Alpha |
| Nvidia | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | - | - | - | $0.00 | $0.00 | 256000 | NVIDIA: Nemotron 3 Nano Omni (free) |
| Poolside | `poolside/laguna-xs.2:free` | - | - | - | $0.00 | $0.00 | 131072 | Poolside: Laguna XS.2 (free) |
| Poolside | `poolside/laguna-m.1:free` | - | - | - | $0.00 | $0.00 | 131072 | Poolside: Laguna M.1 (free) |
| Baidu | `baidu/qianfan-ocr-fast:free` | - | - | - | $0.00 | $0.00 | 65536 | Baidu: Qianfan-OCR-Fast (free) |
| Google | `google/lyria-3-pro-preview` | - | - | - | $0.00 | $0.00 | 1048576 | Google: Lyria 3 Pro Preview |
| Google | `google/lyria-3-clip-preview` | - | - | - | $0.00 | $0.00 | 1048576 | Google: Lyria 3 Clip Preview |
| Openrouter | `openrouter/free` | - | - | - | $0.00 | $0.00 | 200000 | Free Models Router |
| Liquid | `liquid/lfm-2.5-1.2b-thinking:free` | - | - | - | $0.00 | $0.00 | 32768 | LiquidAI: LFM2.5-1.2B-Thinking (free) |
| Liquid | `liquid/lfm-2.5-1.2b-instruct:free` | - | - | - | $0.00 | $0.00 | 32768 | LiquidAI: LFM2.5-1.2B-Instruct (free) |
| Nvidia | `nvidia/nemotron-nano-12b-v2-vl:free` | - | - | - | $0.00 | $0.00 | 128000 | NVIDIA: Nemotron Nano 12B 2 VL (free) |
| Qwen | `qwen/qwen3-next-80b-a3b-instruct:free` | - | - | #102 (72.9%) | $0.00 | $0.00 | 262144 | Qwen: Qwen3 Next 80B A3B Instruct (free) |
| Nvidia | `nvidia/nemotron-nano-9b-v2:free` | - | - | - | $0.00 | $0.00 | 128000 | NVIDIA: Nemotron Nano 9B V2 (free) |
| Cognitivecomputations | `cognitivecomputations/dolphin-mistral-24b-venice-edition:free` | - | - | - | $0.00 | $0.00 | 32768 | Venice: Uncensored (free) |
| Meta-llama | `meta-llama/llama-3.3-70b-instruct:free` | - | - | #156 (50.5%) | $0.00 | $0.00 | 65536 | Meta: Llama 3.3 70B Instruct (free) |
| Meta-llama | `meta-llama/llama-3.2-3b-instruct:free` | - | - | #199 (32.8%) | $0.00 | $0.00 | 131072 | Meta: Llama 3.2 3B Instruct (free) |
| Nousresearch | `nousresearch/hermes-3-llama-3.1-405b:free` | - | - | - | $0.00 | $0.00 | 131072 | Nous: Hermes 3 405B Instruct (free) |
| Meta-llama | `meta-llama/llama-guard-3-8b` | - | - | - | $0.48 | $0.03 | 131072 | Llama Guard 3 8B |
| Mistralai | `mistralai/mistral-nemo` | - | - | - | $0.02 | $0.03 | 131072 | Mistral: Mistral Nemo |
| Meta-llama | `meta-llama/llama-3-8b-instruct` | - | - | - | $0.04 | $0.04 | 8192 | Meta: Llama 3 8B Instruct |
| Sao10k | `sao10k/l3-lunaris-8b` | - | - | - | $0.04 | $0.05 | 8192 | Sao10K: Llama 3 8B Lunaris |
| Meta-llama | `meta-llama/llama-3.1-8b-instruct` | - | - | #204 (30.4%) | $0.02 | $0.05 | 16384 | Meta: Llama 3.1 8B Instruct |
| Gryphe | `gryphe/mythomax-l2-13b` | - | - | - | $0.06 | $0.06 | 4096 | MythoMax 13B |
| Google | `google/gemma-3-4b-it` | - | - | #202 (30.8%) | $0.04 | $0.08 | 131072 | Google: Gemma 3 4B |
| Mistralai | `mistralai/mistral-small-24b-instruct-2501` | - | - | #172 (45.3%) | $0.05 | $0.08 | 32768 | Mistral: Mistral Small 3 |
| Ibm-granite | `ibm-granite/granite-4.1-8b` | - | - | - | $0.05 | $0.10 | 131072 | IBM: Granite 4.1 8B |
| Rekaai | `rekaai/reka-edge` | - | - | - | $0.10 | $0.10 | 16384 | Reka Edge |
| Mistralai | `mistralai/ministral-3b-2512` | - | - | - | $0.10 | $0.10 | 131072 | Mistral: Ministral 3 3B 2512 |
| Z-ai | `z-ai/glm-4-32b` | - | - | - | $0.10 | $0.10 | 128000 | Z.ai: GLM 4 32B  |
| Qwen | `qwen/qwen3-235b-a22b-2507` | - | - | #165 (47.5%) | $0.07 | $0.10 | 262144 | Qwen: Qwen3 235B A22B Instruct 2507 |
| Qwen | `qwen/qwen-2.5-7b-instruct` | - | - | #192 (36.4%) | $0.04 | $0.10 | 32768 | Qwen: Qwen2.5 7B Instruct |
| Ibm-granite | `ibm-granite/granite-4.0-h-micro` | - | - | - | $0.02 | $0.11 | 131000 | IBM: Granite 4.0 Micro |
| Liquid | `liquid/lfm-2-24b-a2b` | - | - | - | $0.03 | $0.12 | 32768 | LiquidAI: LFM2-24B-A2B |
| Google | `google/gemma-3n-e4b-it` | - | - | - | $0.06 | $0.12 | 32768 | Google: Gemma 3n 4B |
| Google | `google/gemma-3-12b-it` | - | - | #183 (40.9%) | $0.04 | $0.13 | 131072 | Google: Gemma 3 12B |
| Qwen | `qwen/qwen-turbo` | - | - | - | $0.03 | $0.13 | 131072 | Qwen: Qwen-Turbo |
| Microsoft | `microsoft/phi-4` | - | - | #145 (56.1%) | $0.07 | $0.14 | 16384 | Microsoft: Phi 4 |
| Amazon | `amazon/nova-micro-v1` | - | - | #187 (40.0%) | $0.04 | $0.14 | 128000 | Amazon: Nova Micro 1.0 |
| Nousresearch | `nousresearch/hermes-2-pro-llama-3-8b` | - | - | - | $0.14 | $0.14 | 8192 | NousResearch: Hermes 2 Pro - Llama-3 8B |
| Qwen | `qwen/qwen3.5-9b` | - | - | #61 (81.7%) | $0.04 | $0.15 | 262144 | Qwen: Qwen3.5-9B |
| Essentialai | `essentialai/rnj-1-instruct` | - | - | - | $0.15 | $0.15 | 32768 | EssentialAI: Rnj 1 Instruct |
| Mistralai | `mistralai/ministral-8b-2512` | - | - | - | $0.15 | $0.15 | 262144 | Mistral: Ministral 3 8B 2512 |
| Arcee-ai | `arcee-ai/trinity-mini` | - | - | - | $0.04 | $0.15 | 131072 | Arcee AI: Trinity Mini |
| Cohere | `cohere/command-r7b-12-2024` | - | - | - | $0.04 | $0.15 | 128000 | Cohere: Command R7B (12-2024) |
| Nvidia | `nvidia/nemotron-nano-9b-v2` | - | - | #134 (64.0%) | $0.04 | $0.16 | 131072 | NVIDIA: Nemotron Nano 9B V2 |
| Google | `google/gemma-3-27b-it` | - | - | #178 (42.4%) | $0.08 | $0.16 | 131072 | Google: Gemma 3 27B |
| Arcee-ai | `arcee-ai/spotlight` | - | - | - | $0.18 | $0.18 | 131072 | Arcee AI: Spotlight |
| Meta-llama | `meta-llama/llama-guard-4-12b` | - | - | - | $0.18 | $0.18 | 163840 | Meta: Llama Guard 4 12B |
| Mistralai | `mistralai/mistral-7b-instruct-v0.1` | - | - | - | $0.11 | $0.19 | 2824 | Mistral: Mistral 7B Instruct v0.1 |
| Mistralai | `mistralai/ministral-14b-2512` | - | - | - | $0.20 | $0.20 | 262144 | Mistral: Ministral 3 14B 2512 |
| Bytedance | `bytedance/ui-tars-1.5-7b` | - | - | - | $0.10 | $0.20 | 128000 | ByteDance: UI-TARS 7B  |
| Mistralai | `mistralai/mistral-small-3.2-24b-instruct` | - | - | #168 (46.1%) | $0.07 | $0.20 | 128000 | Mistral: Mistral Small 3.2 24B |
| Rekaai | `rekaai/reka-flash-3` | - | - | - | $0.10 | $0.20 | 65536 | Reka Flash 3 |
| Meta-llama | `meta-llama/llama-3.2-1b-instruct` | - | - | - | $0.03 | $0.20 | 60000 | Meta: Llama 3.2 1B Instruct |
| Inclusionai | `inclusionai/ling-2.6-flash` | - | - | - | $0.08 | $0.24 | 262144 | inclusionAI: Ling-2.6-flash |
| Qwen | `qwen/qwen3-14b` | - | - | - | $0.06 | $0.24 | 40960 | Qwen: Qwen3 14B |
| Amazon | `amazon/nova-lite-v1` | - | - | #180 (42.0%) | $0.06 | $0.24 | 300000 | Amazon: Nova Lite 1.0 |
| Meta-llama | `meta-llama/llama-3.2-11b-vision-instruct` | - | - | - | $0.24 | $0.24 | 131072 | Meta: Llama 3.2 11B Vision Instruct |
| Tencent | `tencent/hy3-preview` | - | - | - | $0.07 | $0.26 | 262144 | Tencent: Hy3 preview |
| Qwen | `qwen/qwen3.5-flash-02-23` | - | - | - | $0.07 | $0.26 | 1000000 | Qwen: Qwen3.5-Flash |
| Deepseek | `deepseek/deepseek-r1-distill-qwen-32b` | - | - | #135 (62.1%) | $0.29 | $0.29 | 32768 | DeepSeek: R1 Distill Qwen 32B |
| Bytedance-seed | `bytedance-seed/seed-1.6-flash` | - | - | - | $0.07 | $0.30 | 262144 | ByteDance Seed: Seed 1.6 Flash |
| Mistralai | `mistralai/voxtral-small-24b-2507` | - | - | - | $0.10 | $0.30 | 32000 | Mistral: Voxtral Small 24B 2507 |
| Openai | `openai/gpt-oss-safeguard-20b` | - | - | - | $0.07 | $0.30 | 131072 | OpenAI: gpt-oss-safeguard-20b |
| Mistralai | `mistralai/devstral-small` | - | - | - | $0.10 | $0.30 | 131072 | Mistral: Devstral Small 1.1 |
| Meta-llama | `meta-llama/llama-4-scout` | - | - | #144 (57.2%) | $0.08 | $0.30 | 327680 | Meta: Llama 4 Scout |
| Google | `google/gemini-2.0-flash-lite-001` | - | - | #136 (62.1%) | $0.07 | $0.30 | 1048576 | Google: Gemini 2.0 Flash Lite |
| Nousresearch | `nousresearch/hermes-3-llama-3.1-70b` | - | - | - | $0.30 | $0.30 | 131072 | Nous: Hermes 3 70B Instruct |
| Meta-llama | `meta-llama/llama-3.3-70b-instruct` | - | - | #156 (50.5%) | $0.10 | $0.32 | 131072 | Meta: Llama 3.3 70B Instruct |
| Meta-llama | `meta-llama/llama-3.2-3b-instruct` | - | - | #199 (32.8%) | $0.05 | $0.34 | 80000 | Meta: Llama 3.2 3B Instruct |
| Microsoft | `microsoft/phi-4-mini-instruct` | - | - | #145 (56.1%) | $0.08 | $0.35 | 128000 | Microsoft: Phi 4 Mini Instruct |
| Bytedance-seed | `bytedance-seed/seed-2.0-mini` | - | - | - | $0.10 | $0.40 | 262144 | ByteDance Seed: Seed-2.0-Mini |
| Nvidia | `nvidia/llama-3.3-nemotron-super-49b-v1.5` | - | - | #122 (66.7%) | $0.10 | $0.40 | 131072 | NVIDIA: Llama 3.3 Nemotron Super 49B V1.5 |
| Nousresearch | `nousresearch/hermes-4-70b` | - | - | - | $0.13 | $0.40 | 131072 | Nous: Hermes 4 70B |
| Qwen | `qwen/qwen3-8b` | - | - | - | $0.05 | $0.40 | 40960 | Qwen: Qwen3 8B |
| Openai | `openai/gpt-4.1-nano` | - | #113 (0.7) | #158 (50.3%) | $0.10 | $0.40 | 1047576 | OpenAI: GPT-4.1 Nano |
| Google | `google/gemini-2.0-flash-001` | - | - | #136 (62.1%) | $0.10 | $0.40 | 1000000 | Google: Gemini 2.0 Flash |
| Thedrummer | `thedrummer/unslopnemo-12b` | - | - | - | $0.40 | $0.40 | 32768 | TheDrummer: UnslopNemo 12B |
| Qwen | `qwen/qwen-2.5-72b-instruct` | - | - | #162 (49.0%) | $0.36 | $0.40 | 32768 | Qwen2.5 72B Instruct |
| Meta-llama | `meta-llama/llama-3.1-70b-instruct` | - | - | #181 (41.7%) | $0.40 | $0.40 | 131072 | Meta: Llama 3.1 70B Instruct |
| Qwen | `qwen/qwen-vl-plus` | - | - | - | $0.14 | $0.41 | 131072 | Qwen: Qwen VL Plus |
| Qwen | `qwen/qwen3-vl-32b-instruct` | - | - | #116 (68.9%) | $0.10 | $0.42 | 131072 | Qwen: Qwen3 VL 32B Instruct |
| Thedrummer | `thedrummer/rocinante-12b` | - | - | - | $0.17 | $0.43 | 32768 | TheDrummer: Rocinante 12B |
| Arcee-ai | `arcee-ai/trinity-large-preview` | - | - | - | $0.15 | $0.45 | 131000 | Arcee AI: Trinity Large Preview |
| Alibaba | `alibaba/tongyi-deepresearch-30b-a3b` | - | - | - | $0.09 | $0.45 | 131072 | Tongyi DeepResearch 30B A3B |
| Nex-agi | `nex-agi/deepseek-v3.1-nex-n1` | - | - | #141 (59.1%) | $0.14 | $0.50 | 131072 | Nex AGI: DeepSeek V3.1 Nex N1 |
| Allenai | `allenai/olmo-3-32b-think` | - | - | - | $0.15 | $0.50 | 65536 | AllenAI: Olmo 3 32B Think |
| Qwen | `qwen/qwen3-vl-8b-instruct` | - | #124 (-0.7) | - | $0.08 | $0.50 | 131072 | Qwen: Qwen3 VL 8B Instruct |
| Thedrummer | `thedrummer/cydonia-24b-v4.1` | - | - | - | $0.30 | $0.50 | 131072 | TheDrummer: Cydonia 24B V4.1 |
| X-ai | `x-ai/grok-3-mini` | - | #51 (7.9) | #44 (84.6%) | $0.30 | $0.50 | 131072 | xAI: Grok 3 Mini |
| X-ai | `x-ai/grok-3-mini-beta` | - | #51 (7.9) | #44 (84.6%) | $0.30 | $0.50 | 131072 | xAI: Grok 3 Mini Beta |
| Qwen | `qwen/qwen3-vl-30b-a3b-instruct` | - | #117 (0.4) | #108 (70.4%) | $0.13 | $0.52 | 131072 | Qwen: Qwen3 VL 30B A3B Instruct |
| Mistralai | `mistralai/mistral-small-3.1-24b-instruct` | - | - | #170 (46.0%) | $0.35 | $0.56 | 128000 | Mistral: Mistral Small 3.1 24B |
| Tencent | `tencent/hunyuan-a13b-instruct` | - | - | - | $0.14 | $0.57 | 131072 | Tencent: Hunyuan A13B Instruct |
| Mistralai | `mistralai/mistral-small-2603` | - | - | - | $0.15 | $0.60 | 262144 | Mistral: Mistral Small 4 |
| Upstage | `upstage/solar-pro-3` | - | - | - | $0.15 | $0.60 | 128000 | Upstage: Solar Pro 3 |
| Meta-llama | `meta-llama/llama-4-maverick` | - | - | #112 (69.8%) | $0.15 | $0.60 | 1048576 | Meta: Llama 4 Maverick |
| Openai | `openai/gpt-4o-mini-search-preview` | - | - | - | $0.15 | $0.60 | 128000 | OpenAI: GPT-4o-mini Search Preview |
| Mistralai | `mistralai/mistral-saba` | - | - | - | $0.20 | $0.60 | 32768 | Mistral: Saba |
| Cohere | `cohere/command-r-08-2024` | - | - | - | $0.15 | $0.60 | 128000 | Cohere: Command R (08-2024) |
| Openai | `openai/gpt-4o-mini-2024-07-18` | - | - | #186 (40.2%) | $0.15 | $0.60 | 128000 | OpenAI: GPT-4o-mini (2024-07-18) |
| Openai | `openai/gpt-4o-mini` | - | - | #186 (40.2%) | $0.15 | $0.60 | 128000 | OpenAI: GPT-4o-mini |
| Microsoft | `microsoft/wizardlm-2-8x22b` | - | - | - | $0.62 | $0.62 | 65535 | WizardLM-2 8x22B |
| Google | `google/gemma-2-27b-it` | - | - | - | $0.65 | $0.65 | 8192 | Google: Gemma 2 27B |
| Undi95 | `undi95/remm-slerp-l2-13b` | - | - | - | $0.45 | $0.65 | 6144 | ReMM SLERP 13B |
| Meta-llama | `meta-llama/llama-3-70b-instruct` | - | - | - | $0.51 | $0.74 | 8192 | Meta: Llama 3 70B Instruct |
| Qwen | `qwen/qwen2.5-vl-72b-instruct` | - | - | - | $0.25 | $0.75 | 32000 | Qwen: Qwen2.5 VL 72B Instruct |
| Sao10k | `sao10k/l3.3-euryale-70b` | - | - | - | $0.65 | $0.75 | 131072 | Sao10K: Llama 3.3 Euryale 70B |
| Qwen | `qwen/qwen3-next-80b-a3b-thinking` | - | - | #81 (77.2%) | $0.10 | $0.78 | 131072 | Qwen: Qwen3 Next 80B A3B Thinking |
| Qwen | `qwen/qwen-plus-2025-07-28:thinking` | - | - | - | $0.26 | $0.78 | 1000000 | Qwen: Qwen Plus 0728 (thinking) |
| Qwen | `qwen/qwen-plus-2025-07-28` | - | - | - | $0.26 | $0.78 | 1000000 | Qwen: Qwen Plus 0728 |
| Qwen | `qwen/qwen-plus` | - | - | - | $0.26 | $0.78 | 1000000 | Qwen: Qwen-Plus |
| Arcee-ai | `arcee-ai/coder-large` | - | - | - | $0.50 | $0.80 | 32768 | Arcee AI: Coder Large |
| Thedrummer | `thedrummer/skyfall-36b-v2` | - | - | - | $0.55 | $0.80 | 32768 | TheDrummer: Skyfall 36B V2 |
| Deepseek | `deepseek/deepseek-r1-distill-llama-70b` | - | - | #128 (65.2%) | $0.70 | $0.80 | 131072 | DeepSeek: R1 Distill Llama 70B |
| Arcee-ai | `arcee-ai/trinity-large-thinking` | - | - | - | $0.22 | $0.85 | 262144 | Arcee AI: Trinity Large Thinking |
| Sao10k | `sao10k/l3.1-euryale-70b` | - | - | - | $0.85 | $0.85 | 131072 | Sao10K: Llama 3.1 Euryale 70B v2.2 |
| Qwen | `qwen/qwen3-vl-235b-a22b-instruct` | - | #16 (12.7) | - | $0.20 | $0.88 | 262144 | Qwen: Qwen3 VL 235B A22B Instruct |
| Mistralai | `mistralai/codestral-2508` | - | - | - | $0.30 | $0.90 | 256000 | Mistral: Codestral 2508 |
| Deepseek | `deepseek/deepseek-v3.1-terminus` | - | - | #141 (59.1%) | $0.27 | $0.95 | 163840 | DeepSeek: DeepSeek V3.1 Terminus |
| Qwen | `qwen/qwen3.6-35b-a3b` | - | - | #35 (86.0%) | $0.15 | $1.00 | 262144 | Qwen: Qwen3.6 35B A3B |
| Perplexity | `perplexity/sonar` | - | - | - | $1.00 | $1.00 | 127072 | Perplexity: Sonar |
| Qwen | `qwen/qwen-2.5-coder-32b-instruct` | - | - | - | $0.66 | $1.00 | 32768 | Qwen2.5 Coder 32B Instruct |
| Nousresearch | `nousresearch/hermes-3-llama-3.1-405b` | - | - | - | $1.00 | $1.00 | 131072 | Nous: Hermes 3 405B Instruct |
| Mancer | `mancer/weaver` | - | - | - | $0.75 | $1.00 | 8000 | Mancer: Weaver (alpha) |
| Prime-intellect | `prime-intellect/intellect-3` | - | - | - | $0.20 | $1.10 | 131072 | Prime Intellect: INTELLECT-3 |
| Qwen | `qwen/qwen3-next-80b-a3b-instruct` | - | - | #102 (72.9%) | $0.09 | $1.10 | 262144 | Qwen: Qwen3 Next 80B A3B Instruct |
| Minimax | `minimax/minimax-01` | - | - | - | $0.20 | $1.10 | 1000192 | MiniMax: MiniMax-01 |
| Kwaipilot | `kwaipilot/kat-coder-pro-v2` | - | - | - | $0.30 | $1.20 | 256000 | Kwaipilot: KAT-Coder-Pro V2 |
| Morph | `morph/morph-v3-fast` | - | - | - | $0.80 | $1.20 | 81920 | Morph: Morph V3 Fast |
| Arcee-ai | `arcee-ai/virtuoso-large` | - | - | - | $0.75 | $1.20 | 131072 | Arcee AI: Virtuoso Large |
| Alfredpros | `alfredpros/codellama-7b-instruct-solidity` | - | - | - | $0.80 | $1.20 | 4096 | AlfredPros: CodeLLaMa 7B Instruct Solidity |
| Deepcogito | `deepcogito/cogito-v2.1-671b` | - | - | - | $1.25 | $1.25 | 128000 | Deep Cogito: Cogito v2.1 671B |
| Relace | `relace/relace-apply-3` | - | - | - | $0.85 | $1.25 | 256000 | Relace: Relace Apply 3 |
| Anthropic | `anthropic/claude-3-haiku` | - | - | #197 (33.3%) | $0.25 | $1.25 | 200000 | Anthropic: Claude 3 Haiku |
| Qwen | `qwen/qwen3-vl-8b-thinking` | - | #120 (-0.4) | #111 (69.9%) | $0.12 | $1.36 | 131072 | Qwen: Qwen3 VL 8B Thinking |
| Aion-labs | `aion-labs/aion-1.0-mini` | - | - | - | $0.70 | $1.40 | 131072 | AionLabs: Aion-1.0-Mini |
| Sao10k | `sao10k/l3-euryale-70b` | - | - | - | $1.48 | $1.48 | 8192 | Sao10k: Llama 3 Euryale 70B v2.1 |
| Qwen | `qwen/qwen3.6-flash` | - | - | - | $0.25 | $1.50 | 1000000 | Qwen: Qwen3.6 Flash |
| Mistralai | `mistralai/mistral-large-2512` | - | - | - | $0.50 | $1.50 | 262144 | Mistral: Mistral Large 3 2512 |
| Openai | `openai/gpt-3.5-turbo` | - | #82 (5.4) | #201 (30.8%) | $0.50 | $1.50 | 16385 | OpenAI: GPT-3.5 Turbo |
| Qwen | `qwen/qwen3.5-plus-02-15` | - | - | - | $0.26 | $1.56 | 1000000 | Qwen: Qwen3.5 Plus 2026-02-15 |
| Qwen | `qwen/qwen3-vl-30b-a3b-thinking` | - | #112 (0.8) | #92 (74.4%) | $0.13 | $1.56 | 131072 | Qwen: Qwen3 VL 30B A3B Thinking |
| Aion-labs | `aion-labs/aion-2.0` | - | - | - | $0.80 | $1.60 | 131072 | AionLabs: Aion-2.0 |
| Aion-labs | `aion-labs/aion-rp-llama-3.1-8b` | - | - | - | $0.80 | $1.60 | 32768 | AionLabs: Aion-RP 1.0 (8B) |
| Morph | `morph/morph-v3-large` | - | - | - | $0.90 | $1.90 | 262144 | Morph: Morph V3 Large |
| Xiaomi | `xiaomi/mimo-v2.5` | - | - | - | $0.40 | $2.00 | 1048576 | Xiaomi: MiMo-V2.5 |
| Bytedance-seed | `bytedance-seed/seed-2.0-lite` | - | - | #41 (85.1%) | $0.25 | $2.00 | 262144 | ByteDance Seed: Seed-2.0-Lite |
| Bytedance-seed | `bytedance-seed/seed-1.6` | - | - | - | $0.25 | $2.00 | 262144 | ByteDance Seed: Seed 1.6 |
| Mistralai | `mistralai/devstral-2512` | - | - | - | $0.40 | $2.00 | 262144 | Mistral: Devstral 2 2512 |
| Openai | `openai/gpt-5-image-mini` | - | - | - | $2.50 | $2.00 | 400000 | OpenAI: GPT-5 Image Mini |
| Mistralai | `mistralai/mistral-medium-3.1` | - | - | - | $0.40 | $2.00 | 131072 | Mistral: Mistral Medium 3.1 |
| Mistralai | `mistralai/devstral-medium` | - | - | - | $0.40 | $2.00 | 131072 | Mistral: Devstral Medium |
| Mistralai | `mistralai/mistral-medium-3` | - | - | - | $0.40 | $2.00 | 131072 | Mistral: Mistral Medium 3 |
| Openai | `openai/gpt-3.5-turbo-0613` | - | - | - | $1.00 | $2.00 | 4095 | OpenAI: GPT-3.5 Turbo (older v0613) |
| Openai | `openai/gpt-3.5-turbo-instruct` | - | - | - | $1.50 | $2.00 | 4095 | OpenAI: GPT-3.5 Turbo Instruct |
| Qwen | `qwen/qwen-vl-max` | - | - | - | $0.52 | $2.08 | 131072 | Qwen: Qwen VL Max |
| Minimax | `minimax/minimax-m1` | - | - | #114 (69.2%) | $0.40 | $2.20 | 1000000 | MiniMax: MiniMax M1 |
| Qwen | `qwen/qwen3.5-plus-20260420` | - | - | - | $0.40 | $2.40 | 1000000 | Qwen: Qwen3.5 Plus 2026-04-20 |
| Openai | `openai/gpt-audio-mini` | - | - | - | $0.60 | $2.40 | 128000 | OpenAI: GPT Audio Mini |
| Inclusionai | `inclusionai/ling-2.6-1t` | - | - | - | $0.30 | $2.50 | 262144 | inclusionAI: Ling-2.6-1T |
| Amazon | `amazon/nova-2-lite-v1` | - | - | - | $0.30 | $2.50 | 1000000 | Amazon: Nova 2 Lite |
| Qwen | `qwen/qwen3-vl-235b-a22b-thinking` | - | #104 (2.1) | - | $0.26 | $2.60 | 131072 | Qwen: Qwen3 VL 235B A22B Thinking |
| ~google | `~google/gemini-flash-latest` | - | - | - | $0.50 | $3.00 | 1048576 | Google Gemini Flash Latest |
| Xiaomi | `xiaomi/mimo-v2.5-pro` | - | - | - | $1.00 | $3.00 | 1048576 | Xiaomi: MiMo-V2.5-Pro |
| Google | `google/gemini-3.1-flash-image-preview` | - | - | - | $0.50 | $3.00 | 65536 | Google: Nano Banana 2 (Gemini 3.1 Flash Image Preview) |
| Relace | `relace/relace-search` | - | - | - | $1.00 | $3.00 | 256000 | Relace: Relace Search |
| Nousresearch | `nousresearch/hermes-4-405b` | - | - | - | $1.00 | $3.00 | 131072 | Nous: Hermes 4 405B |
| Sao10k | `sao10k/l3.1-70b-hanami-x1` | - | - | - | $3.00 | $3.00 | 16000 | Sao10K: Llama 3.1 70B Hanami x1 |
| Amazon | `amazon/nova-pro-v1` | - | - | #166 (46.9%) | $0.80 | $3.20 | 300000 | Amazon: Nova Pro 1.0 |
| Arcee-ai | `arcee-ai/maestro-reasoning` | - | - | - | $0.90 | $3.30 | 131072 | Arcee AI: Maestro Reasoning |
| Switchpoint | `switchpoint/router` | - | - | - | $0.85 | $3.40 | 131072 | Switchpoint Router |
| ~moonshotai | `~moonshotai/kimi-latest` | - | - | - | $0.75 | $3.50 | 262144 | MoonshotAI Kimi Latest |
| Anthropic | `anthropic/claude-3.5-haiku` | - | - | - | $0.80 | $4.00 | 200000 | Anthropic: Claude 3.5 Haiku |
| Openai | `openai/gpt-3.5-turbo-16k` | - | - | - | $3.00 | $4.00 | 16385 | OpenAI: GPT-3.5 Turbo 16k |
| Qwen | `qwen/qwen-max` | - | - | - | $1.04 | $4.16 | 32768 | Qwen: Qwen-Max  |
| Openai | `openai/o4-mini-high` | - | - | #63 (81.4%) | $1.10 | $4.40 | 200000 | OpenAI: o4 Mini High |
| Openai | `openai/o4-mini` | - | - | #63 (81.4%) | $1.10 | $4.40 | 200000 | OpenAI: o4 Mini |
| Openai | `openai/o3-mini-high` | - | - | #80 (77.2%) | $1.10 | $4.40 | 200000 | OpenAI: o3 Mini High |
| Openai | `openai/o3-mini` | - | - | #80 (77.2%) | $1.10 | $4.40 | 200000 | OpenAI: o3 Mini |
| ~openai | `~openai/gpt-mini-latest` | - | - | - | $0.75 | $4.50 | 400000 | OpenAI GPT Mini Latest |
| ~anthropic | `~anthropic/claude-haiku-latest` | - | - | - | $1.00 | $5.00 | 200000 | Anthropic Claude Haiku Latest |
| Anthropic | `anthropic/claude-haiku-4.5` | - | - | - | $1.00 | $5.00 | 200000 | Anthropic: Claude Haiku 4.5 |
| Anthracite-org | `anthracite-org/magnum-v4-72b` | - | - | - | $3.00 | $5.00 | 16384 | Magnum v4 72B |
| Writer | `writer/palmyra-x5` | - | - | - | $0.60 | $6.00 | 1040000 | Writer: Palmyra X5 |
| Mistralai | `mistralai/mistral-large-2411` | - | - | - | $2.00 | $6.00 | 131072 | Mistral Large 2411 |
| Mistralai | `mistralai/mistral-large-2407` | - | - | - | $2.00 | $6.00 | 131072 | Mistral Large 2407 |
| Mistralai | `mistralai/pixtral-large-2411` | - | - | - | $2.00 | $6.00 | 131072 | Mistral: Pixtral Large 2411 |
| Mistralai | `mistralai/mixtral-8x22b-instruct` | - | - | - | $2.00 | $6.00 | 65536 | Mistral: Mixtral 8x22B Instruct |
| Qwen | `qwen/qwen3.6-max-preview` | - | - | - | $1.04 | $6.24 | 262144 | Qwen: Qwen3.6 Max Preview |
| Mistralai | `mistralai/mistral-medium-3-5` | - | - | - | $1.50 | $7.50 | 262144 | Mistral: Mistral Medium 3.5 |
| Alpindale | `alpindale/goliath-120b` | - | - | - | $3.75 | $7.50 | 6144 | Goliath 120B |
| Openai | `openai/o4-mini-deep-research` | - | - | #63 (81.4%) | $2.00 | $8.00 | 200000 | OpenAI: o4 Mini Deep Research |
| Ai21 | `ai21/jamba-large-1.7` | - | - | - | $2.00 | $8.00 | 256000 | AI21: Jamba Large 1.7 |
| Openai | `openai/o3` | - | - | #52 (83.3%) | $2.00 | $8.00 | 200000 | OpenAI: o3 |
| Perplexity | `perplexity/sonar-reasoning-pro` | - | - | - | $2.00 | $8.00 | 128000 | Perplexity: Sonar Reasoning Pro |
| Perplexity | `perplexity/sonar-deep-research` | - | - | - | $2.00 | $8.00 | 128000 | Perplexity: Sonar Deep Research |
| Aion-labs | `aion-labs/aion-1.0` | - | - | - | $4.00 | $8.00 | 131072 | AionLabs: Aion-1.0 |
| Openai | `openai/gpt-audio` | - | - | - | $2.50 | $10.00 | 128000 | OpenAI: GPT Audio |
| Openai | `openai/gpt-5.1-chat` | - | - | - | $1.25 | $10.00 | 128000 | OpenAI: GPT-5.1 Chat |
| Openai | `openai/gpt-5-image` | - | - | - | $10.00 | $10.00 | 400000 | OpenAI: GPT-5 Image |
| Openai | `openai/gpt-5-codex` | - | - | - | $1.25 | $10.00 | 400000 | OpenAI: GPT-5 Codex |
| Openai | `openai/gpt-4o-audio-preview` | - | - | - | $2.50 | $10.00 | 128000 | OpenAI: GPT-4o Audio |
| Openai | `openai/gpt-5-chat` | - | - | - | $1.25 | $10.00 | 128000 | OpenAI: GPT-5 Chat |
| Cohere | `cohere/command-a` | - | - | - | $2.50 | $10.00 | 256000 | Cohere: Command A |
| Openai | `openai/gpt-4o-search-preview` | - | - | - | $2.50 | $10.00 | 128000 | OpenAI: GPT-4o Search Preview |
| Openai | `openai/gpt-4o-2024-11-20` | - | - | - | $2.50 | $10.00 | 128000 | OpenAI: GPT-4o (2024-11-20) |
| Inflection | `inflection/inflection-3-productivity` | - | - | - | $2.50 | $10.00 | 8000 | Inflection: Inflection 3 Productivity |
| Inflection | `inflection/inflection-3-pi` | - | - | - | $2.50 | $10.00 | 8000 | Inflection: Inflection 3 Pi |
| Cohere | `cohere/command-r-plus-08-2024` | - | - | - | $2.50 | $10.00 | 128000 | Cohere: Command R+ (08-2024) |
| Openai | `openai/gpt-4o-2024-08-06` | - | #126 (-4.2) | #109 (70.1%) | $2.50 | $10.00 | 128000 | OpenAI: GPT-4o (2024-08-06) |
| ~google | `~google/gemini-pro-latest` | - | - | - | $2.00 | $12.00 | 1048576 | Google Gemini Pro Latest |
| Google | `google/gemini-3-pro-image-preview` | - | - | - | $2.00 | $12.00 | 65536 | Google: Nano Banana Pro (Gemini 3 Pro Image Preview) |
| Amazon | `amazon/nova-premier-v1` | - | - | - | $2.50 | $12.50 | 1000000 | Amazon: Nova Premier 1.0 |
| Openai | `openai/gpt-5.2-chat` | - | - | - | $1.75 | $14.00 | 128000 | OpenAI: GPT-5.2 Chat |
| ~anthropic | `~anthropic/claude-sonnet-latest` | - | - | - | $3.00 | $15.00 | 1000000 | Anthropic Claude Sonnet Latest |
| Anthropic | `anthropic/claude-sonnet-4.6` | - | - | - | $3.00 | $15.00 | 1000000 | Anthropic: Claude Sonnet 4.6 |
| Perplexity | `perplexity/sonar-pro-search` | - | - | - | $3.00 | $15.00 | 200000 | Perplexity: Sonar Pro Search |
| Anthropic | `anthropic/claude-sonnet-4.5` | - | - | - | $3.00 | $15.00 | 1000000 | Anthropic: Claude Sonnet 4.5 |
| X-ai | `x-ai/grok-3` | - | #51 (7.9) | #44 (84.6%) | $3.00 | $15.00 | 131072 | xAI: Grok 3 |
| X-ai | `x-ai/grok-3-beta` | - | #51 (7.9) | #44 (84.6%) | $3.00 | $15.00 | 131072 | xAI: Grok 3 Beta |
| Perplexity | `perplexity/sonar-pro` | - | - | - | $3.00 | $15.00 | 200000 | Perplexity: Sonar Pro |
| Anthropic | `anthropic/claude-3.7-sonnet` | - | - | - | $3.00 | $15.00 | 200000 | Anthropic: Claude 3.7 Sonnet |
| Anthropic | `anthropic/claude-3.7-sonnet:thinking` | - | - | - | $3.00 | $15.00 | 200000 | Anthropic: Claude 3.7 Sonnet (thinking) |
| Openai | `openai/gpt-4o-2024-05-13` | - | #109 (1.4) | #148 (53.6%) | $5.00 | $15.00 | 128000 | OpenAI: GPT-4o (2024-05-13) |
| ~anthropic | `~anthropic/claude-opus-latest` | - | - | - | $5.00 | $25.00 | 1000000 | Anthropic: Claude Opus Latest |
| Anthropic | `anthropic/claude-opus-4.7` | - | - | - | $5.00 | $25.00 | 1000000 | Anthropic: Claude Opus 4.7 |
| Anthropic | `anthropic/claude-opus-4.6` | - | - | - | $5.00 | $25.00 | 1000000 | Anthropic: Claude Opus 4.6 |
| Anthropic | `anthropic/claude-opus-4.5` | - | - | - | $5.00 | $25.00 | 200000 | Anthropic: Claude Opus 4.5 |
| Openai | `openai/gpt-chat-latest` | - | - | - | $5.00 | $30.00 | 400000 | OpenAI: GPT Chat Latest |
| ~openai | `~openai/gpt-latest` | - | - | - | $5.00 | $30.00 | 1050000 | OpenAI GPT Latest |
| Openai | `openai/gpt-4-turbo` | - | #111 (1.0) | #164 (48.0%) | $10.00 | $30.00 | 128000 | OpenAI: GPT-4 Turbo |
| Openai | `openai/gpt-4-turbo-preview` | - | - | - | $10.00 | $30.00 | 128000 | OpenAI: GPT-4 Turbo Preview |
| Openai | `openai/gpt-4-1106-preview` | - | - | - | $10.00 | $30.00 | 128000 | OpenAI: GPT-4 Turbo (older v1106) |
| Openai | `openai/o3-deep-research` | - | - | - | $10.00 | $40.00 | 200000 | OpenAI: o3 Deep Research |
| Openai | `openai/o1` | - | - | #78 (78.0%) | $15.00 | $60.00 | 200000 | OpenAI: o1 |
| Openai | `openai/gpt-4-0314` | - | - | - | $30.00 | $60.00 | 8191 | OpenAI: GPT-4 (older v0314) |
| Anthropic | `anthropic/claude-opus-4.1` | - | - | - | $15.00 | $75.00 | 200000 | Anthropic: Claude Opus 4.1 |
| Openai | `openai/o3-pro` | - | - | - | $20.00 | $80.00 | 200000 | OpenAI: o3 Pro |
| Openai | `openai/gpt-5-pro` | - | - | - | $15.00 | $120.00 | 400000 | OpenAI: GPT-5 Pro |
| Anthropic | `anthropic/claude-opus-4.6-fast` | - | - | - | $30.00 | $150.00 | 1000000 | Anthropic: Claude Opus 4.6 (Fast) |
| Openai | `openai/gpt-5.2-pro` | - | - | #5 (93.2%) | $21.00 | $168.00 | 400000 | OpenAI: GPT-5.2 Pro |
| Openai | `openai/o1-pro` | - | - | #75 (79.0%) | $150.00 | $600.00 | 200000 | OpenAI: o1-pro |