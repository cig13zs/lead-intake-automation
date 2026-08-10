"""Self-check for routing + failover logic. Run: python test_router.py"""
import router

PROVIDERS = [
    {"name": "cheap-a", "tier": "cheap", "priority": 1},
    {"name": "cheap-b", "tier": "cheap", "priority": 2},
    {"name": "std-a", "tier": "standard", "priority": 1},
]

def make_send(failing):
    def send(p, prompt, timeout):
        if p["name"] in failing:
            raise RuntimeError("simulated outage")
        return f"ok from {p['name']}", {"input_tokens": 1, "output_tokens": 1}
    return send

# happy path: cheapest wins
text, used = router.route("hi", "cheap", PROVIDERS, make_send(set()))
assert used == "cheap-a", used

# failover within tier
text, used = router.route("hi", "cheap", PROVIDERS, make_send({"cheap-a"}))
assert used == "cheap-b", used

# tier escalation when whole cheap tier is down
text, used = router.route("hi", "cheap", PROVIDERS, make_send({"cheap-a", "cheap-b"}))
assert used == "std-a", used

# start at higher tier skips cheap entirely
text, used = router.route("hi", "standard", PROVIDERS, make_send(set()))
assert used == "std-a", used

# total failure raises with all errors listed
try:
    router.route("hi", "cheap", PROVIDERS, make_send({"cheap-a", "cheap-b", "std-a"}))
    raise AssertionError("should have raised")
except RuntimeError as e:
    assert "cheap-b" in str(e)

print("all checks passed")
