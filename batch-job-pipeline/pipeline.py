#!/usr/bin/env python3
"""Resumable batch pipeline — turn a manifest into N finished outputs overnight.

Point it at a JSON manifest of jobs; each job runs a command that produces one
output file. Already-produced outputs are skipped, so a crashed or interrupted
batch resumes exactly where it stopped by rerunning the same command. Failures
are collected and reported at the end instead of killing the batch.

Built for long-running generation APIs (video/image render jobs, transcription,
report builds) where babysitting 50 sequential jobs by hand is the alternative.

Manifest:
{
  "jobs": [
    {"name": "asset_01",
     "cmd": ["python", "render.py", "--prompt", "...", "-o", "{output}"],
     "output": "out/asset_01.mp4"}
  ]
}
"{output}" inside cmd is replaced with the job's output path.

Usage:
  python pipeline.py manifest.json [--dry-run] [--max-failures N]
"""
import argparse, json, subprocess, sys, time
from pathlib import Path


def run(manifest_path, dry_run=False, max_failures=5, runner=subprocess.run):
    m = json.loads(Path(manifest_path).read_text(encoding="utf-8-sig"))
    jobs, failed, skipped, done = m["jobs"], [], 0, 0

    for job in jobs:
        out = Path(job["output"])
        if out.exists():
            skipped += 1
            print(f"[{job['name']}] SKIP (output exists)")
            continue
        cmd = [c.replace("{output}", str(out)) for c in job["cmd"]]
        print(f"[{job['name']}] run: {' '.join(cmd)}")
        if dry_run:
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        t0 = time.time()
        r = runner(cmd)
        if r.returncode == 0 and out.exists():
            done += 1
            print(f"[{job['name']}] ok ({time.time() - t0:.0f}s)")
        else:
            failed.append(job["name"])
            why = "no output produced" if r.returncode == 0 else f"exit {r.returncode}"
            print(f"[{job['name']}] FAILED ({why})")
            if len(failed) >= max_failures:
                print(f"stopping: {max_failures} failures (systemic problem, not job-level)")
                break

    print(f"\n{done} done, {skipped} skipped, {len(failed)} failed of {len(jobs)}")
    if failed:
        print("failed (rerun the same command to retry just these): " + ", ".join(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-failures", type=int, default=5)
    a = ap.parse_args()
    sys.exit(run(a.manifest, a.dry_run, a.max_failures))
