# Lead intake automation

This is a small n8n portfolio example for an inbound lead workflow.

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
2. Provide `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL` through n8n credentials or environment variables.
3. Replace the example Google Sheet ID and connect the client's own Google credentials.
4. Test with fake data before enabling any live workflow.

## Validate locally

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\validate_workflow.ps1
```

The check verifies the expected nodes and connections, confirms that LLM credentials are referenced through environment variables, and confirms that email is draft-only.

This repository is a portfolio proof, not a claim of production deployment or client revenue. It intentionally contains no credentials, client data, or personal information.
