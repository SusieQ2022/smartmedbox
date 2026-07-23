"""
dashboard.py - caregiver view for SmartMedBox adherence events.

Run from the repository root:

    python src/dashboard.py --host 0.0.0.0 --port 8000

The dashboard reads the same SQLite event log written by store.py/main.py.
It shows structured decisions only; raw camera images are not stored or served.
"""

from argparse import ArgumentParser
from datetime import datetime
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict, List
from urllib.parse import urlparse

try:
    from .config import Config
    from .store import (
        ACTION_ALERT_CAREGIVER,
        ACTION_CONFIRMED,
        ACTION_DUE,
        ACTION_REMIND,
        ACTION_VERIFICATION_FAILED,
        AdherenceStore,
    )
except ImportError:
    from config import Config
    from store import (
        ACTION_ALERT_CAREGIVER,
        ACTION_CONFIRMED,
        ACTION_DUE,
        ACTION_REMIND,
        ACTION_VERIFICATION_FAILED,
        AdherenceStore,
    )


ACTION_PRESENTATION = {
    ACTION_DUE: ("Due", "due"),
    ACTION_REMIND: ("Reminder", "remind"),
    ACTION_ALERT_CAREGIVER: ("Caregiver alert", "alert_caregiver"),
    ACTION_CONFIRMED: ("Confirmed", "confirmed"),
    ACTION_VERIFICATION_FAILED: ("Unverified", "verification_failed"),
    "confirm_taken": ("Confirmed", "confirmed"),
    "taken": ("Confirmed", "confirmed"),
    "late": ("Reminder", "remind"),
    "missed": ("Caregiver alert", "alert_caregiver"),
}


def render_dashboard(summary: Dict[str, int], events: List[Dict]) -> str:
    """Render the caregiver dashboard as a single HTML page."""
    newest_first = list(reversed(events))
    latest = newest_first[0] if newest_first else None

    taken = int(summary.get("taken", 0))
    missed = int(summary.get("missed", 0))
    unverified = int(summary.get("unverified", 0))
    late = int(summary.get("late", 0))
    alerts = int(summary.get("alerts", 0))
    total = int(summary.get("total", 0))

    resolved = taken + missed + unverified
    adherence = round((taken / resolved) * 100) if resolved else 0

    rows = "\n".join(_render_event_row(event) for event in newest_first)
    if not rows:
        rows = (
            '<tr><td colspan="7" class="empty">'
            'No adherence events yet.</td></tr>'
        )

    latest_html = _render_latest_event(latest)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="10">
  <title>SmartMedBox Caregiver Dashboard</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f3f6fb;
      --surface: #ffffff;
      --surface-soft: #f8fafc;
      --ink: #17324d;
      --muted: #6b7a90;
      --line: #dce5ef;
      --brand: #1e4f86;
      --brand-2: #2f80ed;
      --ok: #159447;
      --warn: #d97706;
      --bad: #d92d20;
      --purple: #7c3aed;
      --shadow: 0 10px 30px rgba(31, 66, 110, 0.08);
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      background:
        radial-gradient(circle at top right, rgba(47, 128, 237, 0.08), transparent 28%),
        var(--bg);
      color: var(--ink);
      font-family: Inter, Arial, Helvetica, sans-serif;
    }}

    main {{
      width: min(1180px, calc(100% - 32px));
      margin: 28px auto 40px;
    }}

    header {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 20px;
      margin-bottom: 22px;
    }}

    .brand-row {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}

    .logo {{
      width: 46px;
      height: 46px;
      border-radius: 14px;
      display: grid;
      place-items: center;
      background: linear-gradient(135deg, var(--brand), var(--brand-2));
      color: white;
      font-size: 24px;
      box-shadow: var(--shadow);
    }}

    h1 {{
      margin: 0;
      font-size: clamp(25px, 3vw, 34px);
      line-height: 1.1;
      letter-spacing: -0.02em;
    }}

    .subtle {{
      margin: 7px 0 0;
      color: var(--muted);
      font-size: 14px;
    }}

    .live-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 9px 13px;
      border: 1px solid #b7e2c4;
      border-radius: 999px;
      background: #eefbf2;
      color: #14733a;
      font-size: 13px;
      font-weight: 700;
      white-space: nowrap;
    }}

    .live-dot {{
      width: 9px;
      height: 9px;
      border-radius: 50%;
      background: #22c55e;
      box-shadow: 0 0 0 5px rgba(34, 197, 94, 0.12);
    }}

    .hero-grid {{
      display: grid;
      grid-template-columns: 1.4fr 0.8fr;
      gap: 16px;
      margin-bottom: 18px;
    }}

    .latest-card,
    .adherence-card {{
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 16px;
      box-shadow: var(--shadow);
    }}

    .latest-card {{
      padding: 20px;
      position: relative;
      overflow: hidden;
    }}

    .latest-card::after {{
      content: "";
      position: absolute;
      width: 160px;
      height: 160px;
      border-radius: 50%;
      right: -55px;
      top: -70px;
      background: rgba(47, 128, 237, 0.09);
    }}

    .eyebrow {{
      color: var(--brand-2);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      margin-bottom: 10px;
    }}

    .latest-title {{
      margin: 0 0 6px;
      font-size: 24px;
      position: relative;
      z-index: 1;
    }}

    .latest-meta {{
      color: var(--muted);
      font-size: 14px;
      margin-bottom: 14px;
      position: relative;
      z-index: 1;
    }}

    .latest-message {{
      margin: 0;
      color: #334155;
      line-height: 1.55;
      max-width: 92%;
      position: relative;
      z-index: 1;
    }}

    .adherence-card {{
      padding: 20px;
    }}

    .adherence-number {{
      font-size: 42px;
      font-weight: 800;
      line-height: 1;
      margin: 7px 0 12px;
    }}

    .progress {{
      width: 100%;
      height: 12px;
      border-radius: 999px;
      background: #e8eef5;
      overflow: hidden;
      margin-bottom: 10px;
    }}

    .progress > span {{
      display: block;
      height: 100%;
      width: {adherence}%;
      border-radius: inherit;
      background: linear-gradient(90deg, #17a34a, #48c774);
    }}

    .summary {{
      display: grid;
      grid-template-columns: repeat(5, minmax(130px, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }}

    .metric {{
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 16px;
      box-shadow: 0 6px 20px rgba(31, 66, 110, 0.05);
    }}

    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 13px;
      margin-bottom: 9px;
    }}

    .metric strong {{
      display: block;
      font-size: 31px;
      line-height: 1;
    }}

    .metric.ok strong {{ color: var(--ok); }}
    .metric.warn strong {{ color: var(--warn); }}
    .metric.bad strong {{ color: var(--bad); }}
    .metric.purple strong {{ color: var(--purple); }}
    .metric.info strong {{ color: var(--brand-2); }}

    section {{
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 16px;
      overflow: hidden;
      box-shadow: var(--shadow);
    }}

    .section-head {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 17px 18px;
      border-bottom: 1px solid var(--line);
      background: var(--surface-soft);
    }}

    .section-head h2 {{
      margin: 0;
      font-size: 18px;
    }}

    .section-head span {{
      color: var(--muted);
      font-size: 13px;
    }}

    .table-wrap {{
      overflow-x: auto;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
      min-width: 900px;
    }}

    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 13px 14px;
      text-align: left;
      vertical-align: top;
      font-size: 14px;
      overflow-wrap: anywhere;
    }}

    th {{
      background: #eef4fa;
      color: #3d536b;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    tr:last-child td {{ border-bottom: 0; }}
    tbody tr:hover {{ background: #f8fbff; }}

    .tag {{
      display: inline-block;
      min-width: 104px;
      border-radius: 999px;
      padding: 5px 10px;
      color: #ffffff;
      font-size: 12px;
      font-weight: 700;
      text-align: center;
      white-space: nowrap;
    }}

    .confirmed, .confirm_taken, .taken {{ background: var(--ok); }}
    .due {{ background: var(--brand-2); }}
    .remind, .late {{ background: var(--warn); }}
    .alert_caregiver, .missed {{ background: var(--bad); }}
    .verification_failed {{ background: var(--purple); }}
    .idle {{ background: var(--brand-2); }}

    .alert-yes {{
      color: var(--bad);
      font-weight: 700;
    }}

    .alert-no {{
      color: var(--muted);
    }}

    .empty {{
      color: var(--muted);
      text-align: center;
      padding: 30px;
    }}

    @media (max-width: 900px) {{
      .hero-grid {{ grid-template-columns: 1fr; }}
      .summary {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}

    @media (max-width: 620px) {{
      main {{
        width: min(100% - 18px, 1180px);
        margin: 16px auto 26px;
      }}

      header {{
        flex-direction: column;
      }}

      .summary {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}

      .metric {{
        padding: 14px;
      }}

      .latest-message {{
        max-width: 100%;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <div class="brand-row">
        <div class="logo">✚</div>
        <div>
          <h1>SmartMedBox Caregiver Dashboard</h1>
          <p class="subtle">Today: {total} logged events · Auto-refreshes every 10 seconds</p>
        </div>
      </div>
      <div class="live-badge"><span class="live-dot"></span> Live monitoring</div>
    </header>

    <div class="hero-grid">
      {latest_html}

      <div class="adherence-card">
        <div class="eyebrow">Today's adherence</div>
        <div class="adherence-number">{adherence}%</div>
        <div class="progress"><span></span></div>
        <p class="subtle">{taken} confirmed out of {resolved} resolved medication events</p>
      </div>
    </div>

    <div class="summary">
      {_metric("Taken", taken, "ok")}
      {_metric("Late", late, "warn")}
      {_metric("Missed", missed, "bad")}
      {_metric("Unverified", unverified, "purple")}
      {_metric("Alerts", alerts, "info")}
    </div>

    <section>
      <div class="section-head">
        <h2>Medication history</h2>
        <span>Newest events first</span>
      </div>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th style="width: 14%">Date</th>
              <th style="width: 10%">Time</th>
              <th style="width: 13%">Dose</th>
              <th style="width: 14%">Outcome</th>
              <th style="width: 10%">Overdue</th>
              <th style="width: 9%">Alert</th>
              <th style="width: 30%">Message</th>
            </tr>
          </thead>
          <tbody>
            {rows}
          </tbody>
        </table>
      </div>
    </section>
  </main>
</body>
</html>"""


def _metric(label: str, value: int, css_class: str) -> str:
    return (
        f'<div class="metric {css_class}">'
        f'<span>{escape(label)}</span>'
        f'<strong>{value}</strong>'
        f'</div>'
    )


def _parse_timestamp(ts_value: object) -> tuple[str, str]:
    raw = str(ts_value or "")
    if not raw:
        return "—", "—"

    try:
        parsed = datetime.fromisoformat(raw)
        return parsed.strftime("%d %b %Y"), parsed.strftime("%H:%M:%S")
    except ValueError:
        if "T" in raw:
            date_part, time_part = raw.split("T", 1)
            return date_part, time_part
        return raw, "—"


def _render_latest_event(event: Dict | None) -> str:
    if not event:
        return """
<div class="latest-card">
  <div class="eyebrow">Latest event</div>
  <h2 class="latest-title">No medication events yet</h2>
  <p class="latest-message">Open the medicine box to create the first adherence event.</p>
</div>"""

    raw_action = str(event.get("action") or "idle").lower()
    action_label, action_class = ACTION_PRESENTATION.get(
        raw_action,
        (raw_action.replace("_", " ").title(), "idle"),
    )
    label = escape(str(event.get("label") or f"Compartment {event.get('compartment', '')}"))
    message = escape(str(event.get("message") or "No message recorded."))
    date_text, time_text = _parse_timestamp(event.get("ts"))

    return f"""
<div class="latest-card">
  <div class="eyebrow">Latest event</div>
  <h2 class="latest-title">{label}</h2>
  <div class="latest-meta">
    {escape(date_text)} at {escape(time_text)}
    &nbsp;·&nbsp;
    <span class="tag {action_class}">{escape(action_label)}</span>
  </div>
  <p class="latest-message">{message}</p>
</div>"""


def _render_event_row(event: Dict) -> str:
    raw_action = str(event.get("action") or "idle").lower()
    action_label, action_class = ACTION_PRESENTATION.get(
        raw_action,
        (raw_action.replace("_", " ").title(), "idle"),
    )
    label = escape(str(event.get("label") or f"Compartment {event.get('compartment', '')}"))
    message = escape(str(event.get("message") or ""))
    date_text, time_text = _parse_timestamp(event.get("ts"))
    overdue = int(event.get("minutes_overdue") or 0)
    notified = bool(event.get("notified"))
    alert_text = "Yes" if notified else "No"
    alert_class = "alert-yes" if notified else "alert-no"

    return f"""
<tr>
  <td>{escape(date_text)}</td>
  <td>{escape(time_text)}</td>
  <td>{label}</td>
  <td><span class="tag {action_class}">{escape(action_label)}</span></td>
  <td>{overdue} min</td>
  <td class="{alert_class}">{alert_text}</td>
  <td>{message}</td>
</tr>"""


class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP handler that renders the dashboard from the configured store."""

    store_path = Config.DB_PATH

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path not in ("/", "/index.html"):
            self.send_error(404)
            return

        store = AdherenceStore(self.store_path)
        html = render_dashboard(store.summary_today(), store.events_today())
        body = html.encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        return None


def run_dashboard(
    host: str = "127.0.0.1",
    port: int = 8000,
    db_path: str = Config.DB_PATH,
) -> None:
    DashboardHandler.store_path = db_path
    server = ThreadingHTTPServer((host, port), DashboardHandler)
    print(f"SmartMedBox caregiver dashboard: http://{host}:{port}")
    server.serve_forever()


def main() -> None:
    parser = ArgumentParser(description="Run the SmartMedBox caregiver dashboard.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--db", default=Config.DB_PATH)
    args = parser.parse_args()

    run_dashboard(host=args.host, port=args.port, db_path=args.db)


if __name__ == "__main__":
    main()
