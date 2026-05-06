FROM python:3.11-slim

RUN apt-get update && apt-get install -y git curl wget jq nodejs npm && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir open-interpreter

WORKDIR /workspace/project
ENTRYPOINT ["interpreter"]
