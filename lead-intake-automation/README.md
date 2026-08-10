# Lead Intake Automation (n8n)

An n8n workflow that takes a web form submission, qualifies the lead with an LLM,
pushes it to your CRM, and drafts a personalized follow-up — end to end, with no
human touching a keyboard until the reply is ready to send.

**The problem it solves:** inbound leads sit unanswered for hours while someone
manually reads the form, decides if it's worth chasing, copies it into a CRM, and
writes a reply. Speed-to-lead is the single biggest driver of conversion, and this
closes it to seconds.

## Flow

```
Web form (webhook)  ->  Qualify with LLM  ->  Route on score  ->  CRM + follow-up draft
```

1. **Webhook** receives the form POST at `/lead-intake`.
2. **LLM qualification** scores the lead 1-10 for fit and urgency and returns
   strict JSON: `{score, reason, suggested_reply}`.
3. **Routing** branches on the score so hot leads can trigger an instant alert
   while cold ones are logged quietly.
4. **CRM + draft** files the lead and stores the suggested reply for one-click
   send.

## Import it

1. In n8n: **Workflows -> Import from File -> `lead_intake_workflow.json`**.
2. Set these environment variables (or n8n credentials):
   - `LLM_BASE_URL` — any Anthropic-compatible endpoint
   - `LLM_API_KEY`
   - `LLM_MODEL`
3. Point the CRM node at your system (HubSpot, Airtable, Sheets — swap the node).
4. Activate, then POST a test payload to the webhook URL.

## Notes

- Provider-agnostic: the LLM call uses the standard `/v1/messages` shape, so it
  runs on Anthropic, DeepSeek, Qwen, GLM, or Kimi by changing three env vars.
- The qualification prompt is pinned to JSON-only output so downstream nodes never
  have to parse prose.
- Keys are referenced via `$env`, never hardcoded in the workflow.
