# Verifying hermes-telemetry (after install + enable)

## Structural checks
```
hermes plugins doctor hermes-telemetry   # 12 hooks, no privileged override needed
hermes plugins show hermes-telemetry      # Status: enabled; exposes /stats /budget
```

## Live enforcement check (real spend)
The plugin's `check(scope)` reads current spend from its SQLite DB. For a fresh
install spend is ~0, so expect:
```
BudgetVerdict(scope='global', window='daily', status='ok',
              spent=0.0, limit=5.0, pct=0.0, period_key='YYYY-MM-DD')
```
Reproduce from Python (plugin is not pip-installable standalone; load as package):
```python
import sys, os, types, importlib.util
os.environ["HERMES_HOME"] = "/home/deeone/.hermes"
sys.path.insert(0, "/home/deeone/.hermes/plugins")
pkg = types.ModuleType("htpkg"); pkg.__path__ = ["/home/deeone/.hermes/plugins/hermes-telemetry"]
sys.modules["htpkg"] = pkg
for mod in ["db","paths","budget","pricing"]:
    s = importlib.util.spec_from_file_location(
        f"htpkg.{mod}", f"/home/deeone/.hermes/plugins/hermes-telemetry/{mod}.py")
    m = importlib.util.module_from_spec(s); sys.modules[f"htpkg.{mod}"] = m; s.loader.exec_module(m)
b = sys.modules["htpkg.budget"]
print(b.check("global"))   # reads ~/<home>/telemetry/budget.yaml + SQLite
```
Note: public API is `load_config()` and `check(scope, scope_id="")`, NOT
`load_budget`/`evaluate` (those names do not exist in the module).

## Caveat
Hard cap is a tool-gate, not a mid-call abort. In-flight streams complete and are
billed; further tool work blocked at next boundary; cron jobs paused. Per-cron-job
budgets exclude delegate_task subagent cost — `global` is the true catch-all.
