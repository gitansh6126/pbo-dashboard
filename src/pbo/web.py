"""Zero-dependency web dashboard for the CEO screen, served by Python's http.server.
Reads only the brain on request — no server-side state, your data stays on your machine."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from .reports import full_report

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PBO — CEO Dashboard</title>
<style>
:root{{--bg:#0f1220;--card:#1a1e33;--ink:#e8eaf6;--mut:#9aa1c0;--acc:#7c6cff;--ok:#3ddc97;--warn:#ff9f45;--bad:#ff6b6b;}}
*{{box-sizing:border-box}}body{{margin:0;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--bg);color:var(--ink)}}
header{{padding:22px 28px;background:linear-gradient(90deg,#161b36,#1a1e33);border-bottom:1px solid #2a2f52}}
header h1{{margin:0;font-size:18px;letter-spacing:.5px;color:#fff}}
header .sub{{color:var(--mut);font-size:12px;margin-top:4px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;padding:24px 28px}}
.card{{background:var(--card);border:1px solid #2a2f52;border-radius:14px;padding:18px 20px}}
.card h2{{margin:0 0 12px;font-size:13px;text-transform:uppercase;letter-spacing:1px;color:var(--mut)}}
.kpi{{font-size:30px;font-weight:700}} .kpi small{{font-size:12px;color:var(--mut);font-weight:400}}
.tbl{{width:100%;border-collapse:collapse;font-size:13px}}
.tbl td,.tbl th{{padding:6px 4px;text-align:left;border-bottom:1px solid #262b49}}
.ok{{color:var(--ok)}}.warn{{color:var(--warn)}}.bad{{color:var(--bad)}}.acc{{color:var(--acc)}}
.bar{{height:8px;border-radius:6px;background:#2a2f52;overflow:hidden;margin-top:8px}}
.bar i{{display:block;height:100%;background:linear-gradient(90deg,#7c6cff,#3ddc97)}}
.pill{{display:inline-block;background:#262b49;border-radius:20px;padding:2px 10px;margin:2px;font-size:12px}}
</style></head><body>
<header><h1>◆ PBO — Personal | Business | CEO Operating System</h1>
<div class="sub">local-first · git-diffable markdown brain · as of {as_of}</div></header>
<div class="grid">
  <div class="card"><h2>Personal</h2>
    <div class="kpi">{{todos_open}}<small> open todos</small></div>
    <p><span class="pill">{{contacts}} contacts</span><span class="pill">{{goals}} goals</span></p>
  </div>
  <div class="card"><h2>Businessman</h2>
    <div class="kpi acc">{{pipeline_total:,.0f}}<small> pipeline ${{pipeline_weighted:,.0f}} weighted</small></div>
    <p><span class="pill">{{clients}} clients</span><span class="pill warn">{{approvals_pending}} approvals pending</span></p>
  </div>
  <div class="card"><h2>Business</h2>
    <div class="kpi">{{cash_net_90d:,.0f}}<small> net cash 90d</small></div>
    <p><span class="pill">{{scorecard_on_target}}/{{scorecard_rows}} scorecard on target</span></p>
  </div>
  <div class="card"><h2>CEO</h2>
    <div class="kpi">{{rocks_done}}/{{rocks_total}}<small> rocks done</small></div>
    <div class="bar"><i style="width:{{rock_pct}}%"></i></div>
    <p class="mut">{{rocks_open}} active</p>
  </div>
  <div class="card"><h2>Deal pipeline (weighted ${{pipeline_weighted:,.0f}})</h2>{{pipetable}}</div>
  <div class="card"><h2>Cash-flow drivers (ceos-cashflow)</h2>{{drivers}}</div>
</div>
</body></html>"""


def _html(r):
    keys = dict(r)
    keys["rock_pct"] = round(100 * r["rocks"]["done"] / max(1, r["rocks"]["total"]))
    pipetable = "<table class='tbl'>"
    for st, v in r["pipeline_by_stage"].items():
        pipetable += f"<tr><td>{st}</td><td style='text-align:right'>{v:,.0f}</td></tr>"
    pipetable += "</table>"
    keys["pipetable"] = pipetable or "<span class='mut'>no deals yet</span>"
    drivers = "".join(f"<span class='pill'>{d}</span>" for d in r["cash_drivers"])
    keys["drivers"] = drivers
    return PAGE.format(**keys)


def serve(brain, port=8123):
    rep = full_report(brain)

    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            body = _html(rep).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        def log_message(self, *a):
            pass

    print(f"[pbo] CEO dashboard → http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()