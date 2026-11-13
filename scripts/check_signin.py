"""Refuse to start a round on a Codex sign-in that may expire during it.

Several machines can share one sign-in only while its access token is valid: once it expires, the first copy to renew it makes
the others unusable, and the server can revoke a sign-in whose token another copy renewed even while the token's own date says it
is valid. So the check makes one real, minimal Codex call too, using the sign-in's own folder so that any renewal lands in the
original file. Usage: python3 scripts/check_signin.py AUTH_JSON [--hours 12]. Exits 1 if the sign-in has too little time left or
the server rejects it."""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def hours_left(auth: Path) -> float:
    token = json.loads(auth.read_text())["tokens"]["access_token"]
    payload = token.split(".")[1]
    claims = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    return (claims["exp"] - time.time()) / 3600


def rejection(auth: Path, model: str) -> str:
    """'' if the model answers a one-word request on this sign-in, else the end of Codex's error output."""
    env = {**os.environ, "CODEX_HOME": str(auth.parent)}
    cmd = ["codex", "exec", "--ephemeral", "--skip-git-repo-check", "-s", "read-only", "-m", model, "-"]
    try:
        proc = subprocess.run(cmd, input="Reply with the single word OK.", env=env, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return "no answer within 5 minutes"
    return "" if proc.returncode == 0 and "OK" in proc.stdout else (proc.stderr or proc.stdout)[-600:]


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("auth", type=Path)
    p.add_argument("--hours", type=float, default=12)
    p.add_argument("--model", default="gpt-6.1-sol")
    a = p.parse_args()
    left = hours_left(a.auth)
    print(f"Codex sign-in: {left:.1f} hours left")
    if left < a.hours:
        sys.exit(f"Renew the sign-in first (run any codex command on one machine, then copy its auth.json): fewer than {a.hours:g} hours left.")
    error = rejection(a.auth, a.model)
    if error:
        sys.exit(f"The server rejects this sign-in (renewed elsewhere or revoked); sign in again with `codex login`.\n{error}")
    print("Codex sign-in: accepted by the server")
