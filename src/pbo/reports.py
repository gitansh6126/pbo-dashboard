"""Roll-up reports for the CEO dashboard — merges ceos-scorecard (weekly measurables),
ceos-cashflow (8 drivers), relay's per-client cost roll-up, and PMS state into one view."""
from .core import MODULES
from .agents import execute_goal
import datetime

STAGE_ORDER = ["lead", "qualified", "proposal", "negotiation", "won"]
STAGE_PROB = {"lead": 0.1, "qualified": 0.3, "proposal": 0.5, "negotiation": 0.7, "won": 1.0}
CASH_DRIVERS = ["Net Profit", "Gross Margin", "New Business Development", "Overhead",
                "Sources of Money", "Reduced Operating Expenses", "Debt Service", "Equipment & Assets"]


def weighted_pipeline(brain):
    by_stage = {}
    weighted = 0.0
    for d in brain.list("businessman", "deal"):
        st = (d.get("stage") or "lead").lower()
        by_stage[st] = by_stage.get(st, 0) + float(d.get("value") or 0)
        weighted += float(d.get("value") or 0) * STAGE_PROB.get(st, 0.0)
    return by_stage, weighted


def cash_cliff(brain, horizon_days=90):
    """Net cash position = in net of out within the horizon (aetherion treasury style, offline)."""
    inc = sum(float(c["amount"]) for c in brain.list("business", "cashflow") if (c.get("type") or "in").lower() == "in")
    out = sum(float(c["amount"]) for c in brain.list("business", "cashflow") if (c.get("type") or "in").lower() == "out")
    return inc - out


def scorecard_summary(brain):
    rows, hits = 0, 0
    for s in brain.list("business", "scorecard"):
        rows += 1
        try:
            if float(s["actual"]) >= float(s["target"]):
                hits += 1
        except Exception:
            pass
    return rows, hits


def rocks_status(brain):
    total = open = done = 0
    for r in brain.list("ceo", "rock"):
        total += 1
        st = (r.get("status") or "open").lower()
        if st == "done":
            done += 1
        else:
            open += 1
    return total, open, done


def full_report(brain):
    """Return a dict of everything the CEO screen needs (used by CLI and web)."""
    by_stage, weighted = weighted_pipeline(brain)
    srows, shit = scorecard_summary(brain)
    rocks_total, rocks_open, rocks_done = rocks_status(brain)
    return {
        "as_of": datetime.date.today().isoformat(),
        "todos_open": len(brain.list("personal", "todo", status="open")),
        "contacts": len(brain.list("personal", "contact")),
        "goals": len(brain.list("personal", "goal")),
        "clients": len(brain.list("businessman", "client")),
        "pipeline_by_stage": by_stage,
        "pipeline_total": sum(by_stage.values()),
        "pipeline_weighted": round(weighted, 2),
        "approvals_pending": len(brain.list("businessman", "approval", status="pending")),
        "cash_net_90d": round(cash_cliff(brain), 2),
        "scorecard_rows": srows,
        "scorecard_on_target": shit,
        "rocks": {"total": rocks_total, "open": rocks_open, "done": rocks_done},
        "cash_drivers": CASH_DRIVERS,
    }


def render_cli(brain):
    r = full_report(brain)
    L = []
    L.append("=" * 62)
    L.append(f"  PBO CEO DASHBOARD  —  {r['as_of']}")
    L.append("=" * 62)
    L.append(f"  PERSONAL    todos open: {r['todos_open']}   contacts: {r['contacts']}   goals: {r['goals']}")
    L.append(f"  BUSINESSMAN clients: {r['clients']}   pipeline: {r['pipeline_total']:,.0f}   "
             f"weighted: {r['pipeline_weighted']:,.0f}   approvals pending: {r['approvals_pending']}")
    L.append(f"  BUSINESS    cash net 90d: {r['cash_net_90d']:,.0f}   scorecard: "
             f"{r['scorecard_on_target']}/{r['scorecard_rows']} on target")
    L.append(f"  CEO         rocks: {r['rocks']['done']}/{r['rocks']['total']} done ({r['rocks']['open']} open)")
    L.append("-" * 62)
    if r["pipeline_by_stage"]:
        L.append("  Deal pipeline by stage:")
        for st in STAGE_ORDER:
            if st in r["pipeline_by_stage"] and r["pipeline_by_stage"][st]:
                L.append(f"      {st:<14} {r['pipeline_by_stage'][st]:>10,.0f}")
    L.append("=" * 62)
    return "\n".join(L)