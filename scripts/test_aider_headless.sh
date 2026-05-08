#!/bin/bash
set -e
export AIDER_MODEL="openai/qwen3-35b-uncensored"
export OPENAI_API_BASE="http://127.0.0.1:11434/v1"
export OPENAI_API_KEY="kyberm0nk_2398a369e3e6ad0704d44ba85ea59ba7"
/home/flip/kyberm0nk/docker/aider/venv/bin/aider --no-git --yes --message "Add a dummy file with 'Hello World'" dummy.txt || true
