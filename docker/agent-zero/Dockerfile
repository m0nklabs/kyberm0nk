FROM python:3.11-slim

RUN apt-get update && apt-get install -y git curl wget jq nodejs npm sudo && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/frdel/agent-zero.git /opt/agent-zero && \
    cd /opt/agent-zero && pip install --no-cache-dir -r requirements.txt

WORKDIR /workspace/project
ENTRYPOINT ["python", "/opt/agent-zero/main.py"]
