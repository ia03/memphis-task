"""Assemble a Harbor task directory for one seed."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent

MAIN_DOCKERFILE = """FROM python:3.12-slim
RUN apt-get update \\
    && apt-get install -y --no-install-recommends bash ca-certificates curl procps nodejs npm ripgrep \\
    && rm -rf /var/lib/apt/lists/* \\
    && npm install -g @openai/codex@0.162.1 \\
    && codex --version
RUN useradd -m -d /home/user user
COPY agent_tools/ /home/user/
RUN chown -R user:user /home/user
WORKDIR /home/user
"""

SIM_DOCKERFILE = """FROM python:3.12-slim
RUN apt-get update \\
    && apt-get install -y --no-install-recommends bash ca-certificates curl nodejs npm \\
    && rm -rf /var/lib/apt/lists/* \\
    && npm install -g @openai/codex@0.162.1 \\
    && codex --version
RUN pip install --no-cache-dir "pydantic==2.11.7" "pyyaml==6.0.2" "jsonschema==4.25.1" "rank-bm25==0.2.2" "pillow==11.3.0" "arabic-reshaper==3.0.0"
COPY app/ /app/
WORKDIR /app
ENV PYTHONPATH=/app
CMD ["sh", "-c", "python -m hsim.server --seed $SIM_SEED --out /out --agent-token $SIM_AGENT_TOKEN --grader-token $SIM_GRADER_TOKEN --port 8787"]
"""

SQUID = """http_port 3128
acl openai_api dstdomain .chatgpt.com auth.openai.com api.openai.com
acl tls_port port 443
acl CONNECT method CONNECT
http_access deny CONNECT !tls_port
http_access allow CONNECT openai_api
http_access deny all
cache deny all
access_log stdio:/var/log/squid/access.log
pid_filename /var/run/squid/squid.pid
coredump_dir /var/cache/squid
"""

PROXY_DOCKERFILE = """FROM alpine:3.22
RUN apk add --no-cache squid
COPY squid.conf /etc/squid/squid.conf
RUN mkdir -p /var/run/squid /var/cache/squid /var/log/squid && chown -R squid:squid /var/run/squid /var/cache/squid /var/log/squid
EXPOSE 3128
CMD ["squid", "-N", "-d", "1", "-f", "/etc/squid/squid.conf"]
"""

COMPOSE = """services:
  main:
    environment:
      TASK5_FIELD_URL: http://sim:8787
      TASK5_FIELD_AGENT_TOKEN: ${{SIM_AGENT_TOKEN}}
      HTTPS_PROXY: http://egress:3128
      NO_PROXY: sim,localhost,127.0.0.1
    networks: [corp-net]
    depends_on:
      sim:
        condition: service_healthy
      egress:
        condition: service_healthy
  sim:
    build:
      context: ./sim
    environment:
      SIM_SEED: "{seed}"
      SIM_AGENT_TOKEN: ${{SIM_AGENT_TOKEN}}
      SIM_GRADER_TOKEN: ${{SIM_GRADER_TOKEN}}
      CODEX_HOME: /run/codex
      # The world simulator works in /out/world; this container is its sandbox (Codex's own sandbox does not run in Docker).
      MEMPHIS_SIM_SANDBOX: danger-full-access
      HTTPS_PROXY: http://egress:3128
      NO_PROXY: localhost,127.0.0.1
    volumes:
      - {auth}:/run/codex/auth.json:ro
    networks: [corp-net]
    depends_on:
      egress:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "sh", "-c", "curl -s -o /dev/null -H 'Authorization: Bearer x' http://127.0.0.1:8787/agent/clock"]
      interval: 2s
      timeout: 5s
      retries: 60
  egress:
    build:
      context: ./proxy
    networks: [corp-net, egress-out]
    healthcheck:
      test: ["CMD", "nc", "-z", "127.0.0.1", "3128"]
      interval: 2s
      timeout: 5s
      retries: 30
networks:
  corp-net:
    internal: true
  egress-out: {{}}
"""

TASK_TOML = """schema_version = "1.3"

[metadata]
name = "memphis-first-batch-hidden-state"
seed = {seed}

[agent]
timeout_sec = 43200

[verifier]
timeout_sec = 3600
env = {{ SIM_GRADER_TOKEN = "${{SIM_GRADER_TOKEN}}" }}

[environment]
build_timeout_sec = 1800
env = {{ SIM_AGENT_TOKEN = "${{SIM_AGENT_TOKEN}}", SIM_GRADER_TOKEN = "${{SIM_GRADER_TOKEN}}" }}

[[artifacts]]
source = "/out"
service = "sim"
"""

TEST_SH = """#!/usr/bin/env bash
set -euo pipefail
mkdir -p /logs/verifier
curl -s -X POST -H "Authorization: Bearer $SIM_GRADER_TOKEN" -H "Content-Type: application/json" -d '{}' http://sim:8787/grader/finish > /logs/verifier/score.json
python3 -c "import json; s=json.load(open('/logs/verifier/score.json')); open('/logs/verifier/reward.txt','w').write(str(s['reward']))"
curl -s -H "Authorization: Bearer $SIM_GRADER_TOKEN" http://sim:8787/grader/export > /logs/verifier/export.json
cat /logs/verifier/score.json
"""


def build(seed: int, out: Path, auth: Path, hint: Path | None = None) -> None:
    if out.exists():
        shutil.rmtree(out)
    env = out / "environment"
    (env / "sim" / "app").mkdir(parents=True)
    (env / "proxy").mkdir(parents=True)
    (out / "tests").mkdir(parents=True)
    shutil.copytree(ROOT / "agent_tools", env / "agent_tools", ignore=shutil.ignore_patterns("__pycache__"))
    (env / "Dockerfile").write_text(MAIN_DOCKERFILE)
    app = env / "sim" / "app"
    for name in ("hsim", "world"):
        shutil.copytree(ROOT / name, app / name, ignore=shutil.ignore_patterns("__pycache__"))
    (app / "work" / "catalog").mkdir(parents=True)
    for name in ("october-chats.json", "workers.json", "october-incidents.md", "web-corpus.json"):
        shutil.copyfile(ROOT / "work" / "catalog" / name, app / "work" / "catalog" / name)
    (env / "sim" / "Dockerfile").write_text(SIM_DOCKERFILE)
    (env / "proxy" / "Dockerfile").write_text(PROXY_DOCKERFILE)
    (env / "proxy" / "squid.conf").write_text(SQUID)
    (env / "docker-compose.yaml").write_text(COMPOSE.format(seed=seed, auth=auth))
    (out / "task.toml").write_text(TASK_TOML.format(seed=seed))
    prompt = (ROOT / "world" / "agent_prompt.md").read_text()
    if hint is not None:
        prompt += hint.read_text()
    (out / "instruction.md").write_text(prompt)
    (out / "tests" / "test.sh").write_text(TEST_SH)
    (out / "tests" / "test.sh").chmod(0o755)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--auth", type=Path, default=Path.home() / ".codex" / "auth.json")
    p.add_argument("--hint-file", type=Path, dest="hint_file")
    a = p.parse_args()
    build(a.seed, a.out, a.auth, a.hint_file)
