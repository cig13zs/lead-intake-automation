# Lead intake automation

This is a small n8n demonstration for an inbound lead workflow.

```text
form or webhook -> structured LLM qualification -> hot/nurture routing
                 -> Google Sheets log -> Gmail reply draft
```

The workflow demonstrates:

- a webhook that accepts a lead payload;
- an Anthropic-compatible messages request using environment variables;
- JSON-only qualification output with a parse fallback;
- a score-based routing branch;
- separate hot-lead and nurture sheets;
- a Gmail draft step instead of an uncontrolled email send.

## Import

1. In n8n, choose **Workflows -> Import from File** and select `lead_intake_workflow.json`.
2. Set `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL` as n8n environment variables. To use an n8n credential instead, edit the HTTP Request node after import.
3. Replace the example Google Sheet ID and connect the client's own Google credentials.
4. Test with fake data before enabling any live workflow.

## Validate locally

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\validate_workflow.ps1
```

The structural check verifies the expected nodes and connections, confirms that
LLM credentials are referenced through environment variables, checks that the
fallback validation code is present, and confirms that email is draft-only. It
does not call an LLM, Google Sheets, or Gmail.

## Repository map

- `lead_intake_workflow.json` is the importable n8n example.
- `validate_workflow.ps1` checks its topology and safety boundaries locally.
- `docs/` contains the public walkthrough, service boundary, and clearly
  labelled synthetic failure scenarios.

This workflow has not been deployed for a client or generated revenue. No
credentials, client data, or personal information are included.

## Request a scoped review

If you have a similar workflow problem, open a [workflow review request](https://github.com/cig13zs/lead-intake-automation/issues/new?template=workflow-review.yml). Describe the outcome, trigger, destination, and approximate budget. Do not post credentials, private customer data, API keys, or anything that should not be public.

If this example saves you setup time, you can support maintenance on [Ko-fi](https://ko-fi.com/jju1s).

MIT licensed. See [LICENSE](LICENSE).
