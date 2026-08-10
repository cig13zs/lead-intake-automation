# LLM Cost Router

Routes every LLM request to the cheapest provider that can handle it, fails over
automatically when one is down or rate-limited, and logs every call so spend is
auditable to the cent.

**The problem it solves:** teams wire their app straight to one expensive model
and pay premium rates for work a cheaper tier handles fine — with no fallback when
that provider has an outage. This sits in front of all of them.

## What it does

- **Cheapest-capable-first.** Requests start at the tier you ask for (`cheap`,
  `standard`, `premium`) and escalate only if a provider fails.
- **Automatic failover.** A 429, a timeout, or a 5xx moves to the next provider in
  priority order instead of erroring back to the user.
- **Auditable spend.** Every call appends provider, latency, and token counts to
  `usage.jsonl` — one line per request, ready for a cost report.
- **Provider-agnostic.** Works with any Anthropic-compatible `/v1/messages`
  endpoint: Anthropic, DeepSeek, Qwen/DashScope, GLM, Kimi, or a local gateway.
- **No keys in code.** Providers are declared in `providers.json`; API keys are
  read from environment variables named there.

## Run it

```bash
export ANTHROPIC_API_KEY=...          # names come from providers.json
python router.py "summarize this: ..." --tier cheap
python router.py "design a schema for ..." --tier premium
```

Edit `providers.json` to add or reorder providers (lower `priority` = tried first).

## Test

```bash
python test_router.py
```
Uses an injected fake sender — no network, no keys, no spend. Covers tier
escalation, failover on error, and the log write.

## Files

| File | Purpose |
|---|---|
| `router.py` | The router: `route(prompt, tier, ...)` |
| `providers.json` | Provider list — base URL, model, key env var, priority |
| `usage.jsonl` | Append-only call log |
| `test_router.py` | Offline unit tests |
