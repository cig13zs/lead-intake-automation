#!/usr/bin/env python3
"""LLM cost router — one entry point, N providers, cheapest-capable-first.

Routes each request to the cheapest provider tier that can handle it, fails
over automatically on errors/timeouts/rate limits, and logs every call
(provider, latency, tokens) to a JSONL file so spend is auditable.

Works with any Anthropic-compatible /v1/messages endpoint (Anthropic, DeepSeek,
Qwen/DashScope, GLM, Kimi, local gateways). Providers live in providers.json;
keys live in environment variables, never in code or config.

Usage:
  python router.py "summarize this: ..." --tier cheap
  python router.py "design a database schema for ..." --tier premium
"""
import argparse, json, os, sys, time
from pathlib import Path

import requests

CONFIG = Path(__file__).parent / "providers.json"
LOG = Path(__file__).parent / "usage.jsonl"
TIER_ORDER = ["cheap", "standard", "premium"]


def load_providers():
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    return sorted(cfg["providers"], key=lambda p: p.get("priority", 99))


def _http_send(provider, prompt, timeout):
    key = os.environ.get(provider["api_key_env"], "")
    if not key:
        raise RuntimeError(f"env var {provider['api_key_env']} not set")
    r = requests.post(
        provider["base_url"].rstrip("/") + "/v1/messages",
        headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                 "content-type": "application/json"},
        json={"model": provider["model"], "max_tokens": 2048,
              "messages": [{"role": "user", "content": prompt}]},
        timeout=timeout,
    )
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
    data = r.json()
    text = "".join(b.get("text", "") for b in data.get("content", []))
    usage = data.get("usage", {})
    return text, usage


def route(prompt, tier="cheap", providers=None, send=_http_send, timeout=60):
    """Try providers at `tier`, then escalate tier by tier. Returns
    (text, provider_name). Raises RuntimeError if every provider fails."""
    providers = providers if providers is not None else load_providers()
    start_idx = TIER_ORDER.index(tier)
    errors = []
    for t in TIER_ORDER[start_idx:]:
        for p in [p for p in providers if p["tier"] == t]:
            t0 = time.time()
            try:
                text, usage = send(p, prompt, timeout)
            except Exception as e:  # failover: any provider error tries the next
                errors.append(f"{p['name']}: {e}")
                continue
            _log(p["name"], t, time.time() - t0, usage)
            return text, p["name"]
    raise RuntimeError("all providers failed:\n  " + "\n  ".join(errors))


def _log(name, tier, latency, usage):
    entry = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "provider": name,
             "tier": tier, "latency_s": round(latency, 2),
             "in_tokens": usage.get("input_tokens"),
             "out_tokens": usage.get("output_tokens")}
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt")
    ap.add_argument("--tier", default="cheap", choices=TIER_ORDER)
    args = ap.parse_args()
    text, used = route(args.prompt, args.tier)
    print(f"[{used}]\n{text}")
