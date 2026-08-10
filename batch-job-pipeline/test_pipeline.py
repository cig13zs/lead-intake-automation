"""Self-check: resume-on-rerun and failure collection. Run: python test_pipeline.py"""
import json, sys, tempfile
from pathlib import Path
import pipeline

with tempfile.TemporaryDirectory() as d:
    d = Path(d)
    ok_out, bad_out = d / "ok.txt", d / "bad.txt"
    manifest = d / "m.json"
    manifest.write_text(json.dumps({"jobs": [
        {"name": "good", "output": str(ok_out),
         "cmd": [sys.executable, "-c",
                 f"open(r'{ok_out}', 'w').write('x')"]},
        {"name": "bad", "output": str(bad_out),
         "cmd": [sys.executable, "-c", "raise SystemExit(2)"]},
    ]}))

    rc = pipeline.run(manifest)
    assert rc == 1 and ok_out.exists() and not bad_out.exists()

    # rerun: good job skipped, bad job retried
    calls = []
    class R:  # fake runner records what would run
        def __init__(s, cmd): calls.append(cmd); s.returncode = 2
    rc = pipeline.run(manifest, runner=lambda cmd: R(cmd))
    assert len(calls) == 1, calls  # only the failed job reruns
    assert rc == 1

print("all checks passed")
