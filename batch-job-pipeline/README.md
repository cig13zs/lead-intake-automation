# Resumable Batch Pipeline

Turns a JSON manifest of jobs into N finished files, unattended. If it crashes,
loses power, or you kill it, rerunning the same command picks up exactly where it
stopped — finished outputs are skipped, not redone.

**The problem it solves:** long-running generation work — 50 video renders, a
batch of transcriptions, an overnight report build — where babysitting a
sequential queue by hand is the only alternative, and one failure halfway through
means starting over.

## What it does

- **Resumable by design.** A job whose output file already exists is skipped, so
  the batch is safe to rerun any number of times. No database, no state file — the
  outputs themselves are the checkpoint.
- **Fails safe, not silent.** Failures are collected and reported at the end
  instead of killing the run. A configurable `--max-failures` stops the batch when
  failures look systemic (bad API key) rather than job-level (one bad prompt).
- **Any command.** Each job runs a shell command that produces one output file, so
  it drives any renderer, CLI, or script — not tied to one API.
- **Dry run.** `--dry-run` prints exactly what would execute without spending a
  cent.

## Manifest

```json
{
  "jobs": [
    {"name": "asset_01",
     "cmd": ["python", "render.py", "--prompt", "a cat chef", "-o", "{output}"],
     "output": "out/asset_01.mp4"}
  ]
}
```
`{output}` inside `cmd` is replaced with the job's output path.

## Run it

```bash
python pipeline.py manifest.json            # run the batch
python pipeline.py manifest.json --dry-run  # preview only
python pipeline.py manifest.json --max-failures 3
```

## Test

```bash
python test_pipeline.py
```
Injects a fake runner — no real jobs execute. Covers skip-on-exists, resume,
failure collection, and the max-failures stop.
