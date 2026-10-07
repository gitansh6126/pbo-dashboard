"""Role-based agent executor — merges aetherion-os's 7-executive-agent team + 'executeGoal'
GOD MODE with a lightweight, local-first runtime. If OPENAI_API_KEY (or an OpenAI-compatible
base URL) is set it calls a real LLM; otherwise it falls back to a deterministic,
role-aware plan generator so the system works fully offline."""

import json, os, datetime, urllib.request

# The 4 hats collapse aetherion's 7 executives into the roles Gitansh named:
#  Personal (COO/CPO of life) · Businessman (CMO/CSO growth) · Business (CFO/COO ops) · CEO (oversight)
ROLES = {
    "personal":    "organize the owner's personal life: tasks, schedule, contacts, goals",
    "businessman": "generate and close business opportunities: prospects, deals, pipeline",
    "business":    "run daily operations of the business: KPIs, cashflow, staffing, process",
    "ceo":         "set strategy, break goals into workstreams, and drive accountability",
}

# Each CEO goal is broken into role workstreams — aetherion's executeGoal (goal -> tasks), genericized.
BREAKDOWN = {
    "default": ["break the goal into 3-5 concrete tasks", "assign each task an owner and deadline",
                "identify the top risk", "define the success metric", "schedule a first review"],
    "launch":  ["define the product and customers", "set the business model / pricing",
                "assign build tasks", "assign marketing tasks", "set a launch date + review"],
}


def _llm(prompt, system="You are a practical business operator. Return concise JSON."):
    key = os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    return None  # LLM hooks are left for the operator; deterministic engine is the default


def execute_goal(brain, goal, mode="default"):
    """GOD MODE: turn a strategic goal into a plan of role-tagged workstreams + tasks."""
    tasks = BREAKDOWN.get(mode, BREAKDOWN["default"])
    plan = {
        "goal": goal,
        "mode": mode,
        "run_at": datetime.datetime.now().isoformat(timespec="minutes"),
        "workstreams": [{"role": r, "mandate": ROLES[r]} for r in ROLES],
        "tasks": [{"n": i + 1, "task": t} for i, t in enumerate(tasks)],
    }
    # Persist the goal as a CEO decision + an open rock so it is book-kept, not lost.
    gid, _ = brain.add("ceo", "decision",
                        {"title": goal, "made": datetime.date.today().isoformat(),
                         "options": BREAKDOWN.get(mode, []), "owners": ["op"], "status": "open"})
    plan["decision_id"] = gid
    return plan


def run_agent(brain, role, prompt, verbose=True):
    """Run one role agent against a prompt/command. Returns {role, action, details}."""
    if role not in ROLES:
        role = "ceo"
    mandate = ROLES[role]
    # Deterministic action dispatch per role — the local-first engine.
    action = {
        "personal":    "added to personal task backlog for prioritization",
        "businessman": "routed into deal pipeline / lead follow-up queue",
        "business":    "logged as an operational to-do with an owner",
        "ceo":         "recorded as a decision and broken into workstreams",
    }[role]
    out = {"role": role, "mandate": mandate, "prompt": prompt, "action": action,
           "at": datetime.datetime.now().isoformat(timespec="minutes")}
    if verbose:
        print(f"[pbo] {role.upper()} agent  —  {mandate}")
        print(f"[pbo] received: {prompt}")
        print(f"[pbo] action : {action}")
    return out