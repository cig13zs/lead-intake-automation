param(
    [string]$WorkflowPath = (Join-Path $PSScriptRoot 'lead_intake_workflow.json')
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $WorkflowPath -PathType Leaf)) {
    throw "Workflow file not found: $WorkflowPath"
}

$raw = Get-Content -LiteralPath $WorkflowPath -Raw
$workflow = $raw | ConvertFrom-Json
$issues = [System.Collections.Generic.List[string]]::new()

$requiredNodes = @(
    'Lead form webhook',
    'Qualify lead (LLM)',
    'Parse qualification',
    'Hot lead?',
    'CRM: hot leads',
    'Draft follow-up email',
    'CRM: nurture list'
)
$actualNodes = @($workflow.nodes | ForEach-Object { $_.name })

foreach ($name in $requiredNodes) {
    if ($actualNodes -notcontains $name) {
        $issues.Add("missing node: $name")
    }
}

foreach ($source in @('Lead form webhook', 'Qualify lead (LLM)', 'Parse qualification', 'Hot lead?')) {
    if (-not $workflow.connections.PSObject.Properties.Name.Contains($source)) {
        $issues.Add("missing connection source: $source")
    }
}

foreach ($token in @('LLM_BASE_URL', 'LLM_API_KEY', 'LLM_MODEL')) {
    if ($raw -notmatch [regex]::Escape("`$env.$token")) {
        $issues.Add("missing environment reference: $token")
    }
}

if ($raw -match 'sk-[A-Za-z0-9]+' -or $raw -match 'xox[baprs]-[A-Za-z0-9-]+') {
    $issues.Add('possible hardcoded credential detected')
}

$draftNode = @($workflow.nodes | Where-Object { $_.name -eq 'Draft follow-up email' })
if ($draftNode.Count -ne 1 -or $draftNode[0].parameters.resource -ne 'draft') {
    $issues.Add('email step is not configured as a Gmail draft')
}

$parseNode = @($workflow.nodes | Where-Object { $_.name -eq 'Parse qualification' })
if ($parseNode.Count -ne 1 -or $parseNode[0].parameters.jsCode -notmatch 'qualificationValid') {
    $issues.Add('qualification output validation is missing')
}
if ($parseNode.Count -ne 1 -or $parseNode[0].parameters.jsCode -notmatch 'leadValid') {
    $issues.Add('lead name and email validation is missing')
}

if ($workflow.settings.executionOrder -ne 'v1') {
    $issues.Add('unexpected n8n execution order')
}

if ($issues.Count -gt 0) {
    $issues | ForEach-Object { "FAIL: $_" }
    exit 1
}

"PASS: valid JSON"
"PASS: $($actualNodes.Count) expected workflow nodes present"
"PASS: webhook, qualification, parse, and routing connections present"
"PASS: LLM credentials are referenced through environment variables"
"PASS: lead fields and qualification output have an explicit fallback"
"PASS: follow-up email is draft-only"
"PASS: no hardcoded credential pattern found"
