FROM python:3.12-slim

# Unified system dependencies (build-essential, nodejs, etc.)
RUN apt-get update && apt-get install -y \
    git curl wget jq nodejs npm sudo build-essential python3-dev python3-tk \
    && rm -rf /var/lib/apt/lists/*

# Install JavaScript CLIs used by Superset and premium coding-agent evaluation.
RUN npm install -g bun @anthropic-ai/claude-code

# Upgrade pip and pre-install heavy math/ML dependencies for Agent Zero
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir numpy scikit-learn

# Install Aider & OpenCode
RUN pip install --no-cache-dir aider-chat open-interpreter

# Install Agent Zero
RUN git clone https://github.com/frdel/agent-zero.git /opt/agent-zero && \
    cd /opt/agent-zero && pip install --no-cache-dir -r requirements.txt

# AZ Telegram plugin requires `uv` to bootstrap aiogram on first use.
# Pre-install both so the plugin works without runtime network installs.
# Note: aiogram pulls httpx>=0.28 transitively, so the httpx pin must
# come AFTER this layer to win.
RUN pip install --no-cache-dir uv && \
    uv pip install --system aiogram

# Pin httpx<0.28: openai 1.42 / litellm 1.44 still pass `proxies` kwarg
# which httpx 0.28+ removed. Without this, all chat completions fail.
# MUST be the last pip layer touching httpx.
RUN pip install --no-cache-dir "httpx<0.28"

# Create a shared config directory inside the container
RUN mkdir -p /config/aider /config/opencode /config/agent-zero

WORKDIR /workspace/project

# Keep container alive
ENTRYPOINT ["tail", "-f", "/dev/null"]

# Install GitHub CLI (gh) for repository rights & automation
RUN mkdir -p -m 755 /etc/apt/keyrings && \
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null && \
    chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && apt-get install -y gh && \
    rm -rf /var/lib/apt/lists/*
