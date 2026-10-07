#!/usr/bin/env python3
"""pbo — Personal | Business | CEO Operating System CLI.

Usage:
  pbo init [--dir brain]
  pbo add <module>.<type> --title ... [--owner ...] [extra k=v ...]
  pbo list [module.type] [--status open]
  pbo do <module>.<type> <id|title>
  pbo run <role> "<prompt>"
  pbo plan "<strategic goal>" [--mode launch]
  pbo report
  pbo web [--port 8123]
"""
import argparse, sys, os
from .core import Brain, MODULES
from .agents import run_agent, execute_goal
from .reports import render_cli

DEFAULT_DIR = os.path.join(os.getcwd(), "brain")


def _resolve(brain, spec, ident):
    if "." in spec:
        m, t = spec.split(".", 1)
    else:
        m = spec
        t = None
    hits = [r for r in brain.list(m, t) if r["_id"] == ident or
            (r.get("title") or r.get("name") or "").lower() == ident.lower()]
    if not hits:
        sys.exit(f"not found: {spec} {ident}")
    return hits[0]


def cmd_add(brain, a):
    m, t = a.kind.split(".", 1)
    keys = {k: v for k, v in (z.split("=", 1) for z in a.extra or [])}
    data = {"title": a.title or a.name or keys.pop("title", "")}
    if a.owner:
        data["owner"] = a.owner
    data.update(keys)
    eid, path = brain.add(m, t, data, body=a.body or "")
    print(f"added {m}.{t}  id={eid}")
    print(f"  {path}")


def cmd_list(brain, a):
    if a.spec and "." in a.spec:
        m, t = a.spec.split(".", 1)
        cols = [c for c in MODULES[m][t] if c != "status"]
    else:
        m, t = (a.spec or None), None
        cols = ["title", "status"]
    for r in brain.list(m, t, status=(a.status if a.status else None)):
        vals = ", ".join(f"{c}={r.get(c, '')}" for c in cols[:4] if r.get(c))
        print(f"[{r['_module']}.{r['_type']}] {vals}" + ("   :: " + ", ".join(f"{c}={r[c]}" for c in ["status"] if c in r and r.get(c))))


def cmd_do(brain, a):
    r = _resolve(brain, a.spec, a.ident)
    brain.update(r["_module"], r["_type"], r["_id"], {"status": a.status})
    print(f"marked {r['_module']}.{r['_type']} '{r.get(a.status and 'title') or r.get('title', r['_id'])}' -> {a.status}")


def build_parser():
    p = argparse.ArgumentParser(prog="pbo", description="Personal | Business | CEO Operating System")
    p.add_argument("--dir", default=DEFAULT_DIR, help="brain data directory (default: ./brain)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init")
    s.set_defaults(fn=lambda b, a: print(f"brain ready at {b.root}"))

    s = sub.add_parser("add")
    s.add_argument("kind", help="module.entity, e.g. personal.todo")
    s.add_argument("--title", help="title (also: name/metric)")
    s.add_argument("--name", dest="title")
    s.add_argument("--owner")
    s.add_argument("--body", help="freeform notes")
    s.add_argument("extra", nargs="*", help="extra k=v fields")
    s.set_defaults(fn=cmd_add)

    s = sub.add_parser("list")
    s.add_argument("spec", nargs="?", help="optional module.type")
    s.add_argument("--status")
    s.set_defaults(fn=cmd_list)

    s = sub.add_parser("do")
    s.add_argument("spec")
    s.add_argument("ident")
    s.add_argument("--status", default="done")
    s.set_defaults(fn=cmd_do)

    s = sub.add_parser("run")
    s.add_argument("role", choices=["personal", "businessman", "business", "ceo"])
    s.add_argument("prompt")
    s.set_defaults(fn=lambda b, a: print(run_agent(b, a.role, a.prompt)["action"]))

    s = sub.add_parser("plan")
    s.add_argument("goal")
    s.add_argument("--mode", default="default", choices=["default", "launch"])
    s.set_defaults(fn=lambda b, a: _plan(b, a))

    s = sub.add_parser("report")
    s.set_defaults(fn=lambda b, a: print(render_cli(b)))

    s = sub.add_parser("web")
    s.add_argument("--port", type=int, default=8123)
    s.set_defaults(fn=lambda b, a: _web(b, a))
    return p


def _plan(b, a):
    plan = execute_goal(b, a.goal, mode=a.mode)
    print(f"GOAL: {plan['goal']}  ({plan['mode']} mode)")
    print(f"run at {plan['run_at']} | decision id {plan['decision_id']}")
    print("workstreams:", ", ".join(f"{w['role']}({w['mandate'][:28]})" for w in plan["workstreams"]))
    for t in plan["tasks"]:
        print(f"  {t['n']}. {t['task']}")


def _web(b, a):
    from .web import serve
    serve(b, a.port)


def main(argv=None):
    a = build_parser().parse_args(argv)
    b = Brain(a.dir if a.dir else DEFAULT_DIR)
    a.fn(b, a)


if __name__ == "__main__":
    main()