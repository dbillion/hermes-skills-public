"""
Reusable NotebookLM RAG refill / query runner with multi-account rotation.

WHY THIS EXISTS (verified this session):
- Free-tier NotebookLM quota is PER-ACCOUNT (~50 queries/day). Rotating across N accounts
  gives ~N x 50. Login alone is NOT enough: each account also needs (a) NotebookLM web opened
  once and (b) an editor invite on the target notebook from the owner. PERMISSION_DENIED means
  invite/web-gate missing; RATE means wait-for-reset. Do NOT treat PERMISSION_DENIED as RATE.
- Run ONE serialized process. Parallel background runs on the same accounts DOUBLE-THROTTLE.

USAGE:
  python3 query_rag_rotate.py
Edit NB_A / NB_B / PROFILES / MISSING / QS below for the task. The runner only fetches the
MISSING list (checks existing <qid>_<side>.txt > 500B and skips). Skips any account returning
RATE/PERMISSION_DENIED and rotates to the next; waits only if ALL are blocked.

Requires `nlm` on PATH (set PATH to include ~/.local/bin in env).
"""
import subprocess, time, os

NB_A = "NOTEBOOK_A_ID"
NB_B = "NOTEBOOK_B_ID"
OUT = "/tmp/colornote_work/analysis"
PROFILES = ["dayozoe", "abiodun", "mentoratechies", "adeoyeoludayo53", "oludayoadeoye35",
            "oludayoadeoye99", "dayo4ai", "dayoglorious", "architectlead7"]
os.makedirs(OUT, exist_ok=True)

# Map each query id -> the question text sent to NotebookLM.
QS = {
    "Q8_character_strengths": "Using the VIA Character Strengths framework ...",
    # ... fill in per task ...
}
# (qid, notebook_id, side) entries to fetch; skip any already >500B on disk.
MISSING = [
    # ("Q8_character_strengths", NB_A, "A"),
    # ("Q8_character_strengths", NB_B, "B"),
]

env = dict(os.environ)
env['PATH'] = '/home/deeone/.local/bin:' + env.get('PATH', '')


def query(nb, q, profile):
    cmd = ["nlm", "query", "notebook", "--json", nb, q, "--profile", profile, "--timeout", "180"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=220)
        out = (r.stdout or '') + (r.stderr or '')
        if '"answer"' in out and out.strip().startswith('{') and 'usage limit' not in out.lower() \
           and 'PERMISSION_DENIED' not in out:
            return ("OK", out.strip())
        if 'usage limit' in out.lower() or 'PERMISSION_DENIED' in out or 'RESOURCE_EXHAUSTED' in out:
            return ("BLOCKED", out[:80])
        return ("ERR", out[:120])
    except subprocess.TimeoutExpired:
        return ("TIMEOUT", "")


pi = 0
for qid, nb, side in MISSING:
    path = f"{OUT}/{qid}_{side}.txt"
    if os.path.exists(path) and os.path.getsize(path) > 500:
        print(f"skip {qid} {side} (have)"); continue
    done = False
    for off in range(len(PROFILES)):
        profile = PROFILES[(pi + off) % len(PROFILES)]
        status, res = query(nb, QS[qid], profile)
        if status == "OK":
            with open(path, "w") as f:
                f.write(res)
            print(f"### {qid} {side} [{profile}] OK {len(res)}B")
            done = True
            pi += 1
            break
        else:
            print(f"  {profile}: {status}, next")
    if not done:
        print(f"### {qid} {side}: ALL BLOCKED — wait 600s")
        time.sleep(600)
    time.sleep(20)

# rebuild combined files for every qid in QS
for qid in QS:
    a = open(f"{OUT}/{qid}_A.txt").read() if os.path.exists(f"{OUT}/{qid}_A.txt") else ""
    b = open(f"{OUT}/{qid}_B.txt").read() if os.path.exists(f"{OUT}/{qid}_B.txt") else ""
    with open(f"{OUT}/{qid}_combined.txt", "w") as f:
        f.write("=== NOTEBOOK A ===\n\n" + a + "\n\n=== NOTEBOOK B ===\n\n" + b)
print("=== RAG ROTATE DONE ===")
