"""Infinite-brain-style storage: every entity is a git-diffable Markdown file with a
JSON header, so humans can read/edit it and any file-reading agent can act on it.
No database, no server, no vendor lock-in (infinite-brain-os / ceos philosophy)."""
import json, re, os, time, uuid

HEAD_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)

# Central schema: module -> entity type -> fields. Keeps add/list/update generic.
# The field set for each type reflects the BEST deduped model for that task.
MODULES = {
    "personal": {
        "todo":     ["title", "owner", "due", "priority", "status"],
        "contact":  ["name", "phone", "email", "company", "note"],
        "calendar": ["title", "date", "start", "end", "attendees"],
        "goal":     ["title", "target", "deadline", "progress", "status"],
        "note":     ["title", "tags"],
    },
    "businessman": {
        "client":   ["name", "contact", "wsp", "status", "note"],
        "deal":     ["title", "client", "value", "stage", "owner", "probability"],
        "approval": ["title", "client", "amount", "status", "kind"],
        "cost":     ["title", "category", "amount", "client", "date"],
    },
    "business": {
        "scorecard":["metric", "target", "actual", "period", "owner"],
        "cashflow": ["driver", "amount", "period", "type", "note"],
        "org":      ["seat", "owner", "roles"],
        "process":  ["title", "steps", "owner"],
    },
    "ceo": {
        "vto":      ["element", "content", "updated"],
        "rock":     ["title", "owner", "outcome", "quarter", "status"],
        "issue":    ["title", "desc", "flow", "status"],
        "meeting":  ["title", "date", "type", "notes"],
        "decision": ["title", "made", "options", "owners", "status"],
    },
}

VALID_STATUS = {"open", "done", "in_progress", "blocked", "won", "lost", "accepted", "rejected"}


def _idslug(s):
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return s[:40] or "item"


def _new_id(module, etype):
    return f"{module[:1]}-{etype[:2]}-{int(time.time())}-{uuid.uuid4().hex[:4]}"


class Brain:
    """Filesystem-backed store rooted at <root>/. Data lives at <root>/<module>/<etype>/<id>.md"""

    def __init__(self, root):
        self.root = os.path.abspath(root)
        os.makedirs(self.root, exist_ok=True)

    def _path(self, module, etype, eid):
        return os.path.join(self.root, module, etype, f"{_idslug(eid)}.md")

    # ---- CRUD ----
    def add(self, module, etype, data, body=""):
        assert module in MODULES and etype in MODULES[module], f"unknown {module}.{etype}"
        d = dict(data)
        d.setdefault("id", _new_id(module, etype))
        d.setdefault("status", "open")
        d.setdefault("created", time.strftime("%Y-%m-%d"))
        p = self._path(module, etype, d["id"])
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write("---\n" + json.dumps(d, indent=2, default=str) + "\n---\n\n" + (body or ""))
        return d["id"], p

    def update(self, module, etype, eid, data):
        d = self.get(module, etype, eid)
        if d is None:
            raise KeyError(f"{module}.{etype}:{eid} not found")
        d.update(data)
        d["updated"] = time.strftime("%Y-%m-%d")
        p = self._path(module, etype, eid)
        with open(p, "w", encoding="utf-8") as f:
            f.write("---\n" + json.dumps(d, indent=2, default=str) + "\n---\n\n")
        return d

    def get(self, module, etype, eid):
        p = self._path(module, etype, eid)
        if not os.path.exists(p):
            return None
        m = HEAD_RE.match(open(p, encoding="utf-8").read())
        return json.loads(m.group(1)) if m else None

    def list(self, module=None, etype=None, status=None):
        out = []
        for mod in ([module] if module else MODULES):
            moddir = os.path.join(self.root, mod)
            if not os.path.isdir(moddir):
                continue
            for et in ([etype] if etype else os.listdir(moddir)):
                if et == "export" or et.startswith("."):
                    continue
                tdir = os.path.join(moddir, et)
                if not os.path.isdir(tdir):
                    continue
                for fn in os.listdir(tdir):
                    if not fn.endswith(".md"):
                        continue
                    m = HEAD_RE.match(open(os.path.join(tdir, fn), encoding="utf-8").read())
                    if m:
                        rec = json.loads(m.group(1))
                        rec["_module"], rec["_type"], rec["_id"] = mod, et, rec.get("id")
                        if status and rec.get("status") != status:
                            continue
                        out.append(rec)
        return out

    def counts(self):
        c = {"total": 0}
        for rec in self.list():
            m, t = rec["_module"], rec["_type"]
            c[m] = c.get(m, {})
            c[m][t] = c[m].get(t, 0) + 1
            c["total"] += 1
        return c