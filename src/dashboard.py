"""
dashboard.py - caregiver view for SmartMedBox adherence events.

Run from the repository root:

    python src/dashboard.py --port 8000

The dashboard reads the same SQLite event log written by store.py/main.py.
It shows structured decisions only; raw camera images are not stored or served.
"""

from argparse import ArgumentParser
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict, List
from urllib.parse import urlparse

try:
    from .config import Config
    from .store import AdherenceStore
except ImportError:
    from config import Config
    from store import AdherenceStore


def render_dashboard(summary: Dict[str, int], events: List[Dict]) -> str:
    """Render the caregiver dashboard as a single HTML page."""
    rows = "\n".join(_render_event_row(event) for event in events)
    if not rows:
        rows = (
            "<tr><td colspan=\"6\" class=\"empty\">No adherence events yet.</td>"
            "</tr>"
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="30">
  <title>SmartMedBox Caregiver Dashboard</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f7f9;
      --surface: #ffffff;
      --ink: #1f2937;
      --muted: #667085;
      --line: #d8dde6;
      --ok: #15803d;
      --warn: #b45309;
      --bad: #b91c1c;
      --info: #2563eb;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Arial, Helvetica, sans-serif;
      letter-spacing: 0;
    }}
    main {{
      width: min(1120px, calc(100% - 32px));
      margin: 24px auto;
    }}
    header {{
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 18px;
    }}
    h1 {{
      margin: 0;
      font-size: 28px;
      line-height: 1.15;
    }}
    .subtle {{
      margin: 6px 0 0;
      color: var(--muted);
      font-size: 14px;
    }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(5, minmax(120px, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }}
    .metric {{
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 13px;
      margin-bottom: 8px;
    }}
    .metric strong {{
      display: block;
      font-size: 30px;
      line-height: 1;
    }}
    section {{
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 12px 14px;
      text-align: left;
      vertical-align: top;
      font-size: 14px;
      overflow-wrap: anywhere;
    }}
    th {{
      background: #eef2f7;
      color: #344054;
      font-size: 12px;
      text-transform: uppercase;
    }}
    tr:last-child td {{ border-bottom: 0; }}
    .tag {{
      display: inline-block;
      min-width: 98px;
      border-radius: 999px;
      padding: 4px 8px;
      color: #ffffff;
      font-size: 12px;
      text-align: center;
      white-space: nowrap;
    }}
    .confirm_taken, .taken {{ background: var(--ok); }}
    .remind, .late {{ background: var(--warn); }}
    .alert_caregiver, .missed {{ background: var(--bad); }}
    .warn_double, .double {{ background: #7c3aed; }}
    .idle {{ background: var(--info); }}
    .empty {{
      color: var(--muted);
      text-align: center;
      padding: 28px;
    }}
    @media (max-width: 760px) {{
      main {{ width: min(100% - 20px, 1120px); margin: 16px auto; }}
      header {{ align-items: start; flex-direction: column; }}
      .summary {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      table {{ table-layout: auto; }}
      th:nth-child(4), td:nth-child(4) {{ display: none; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>SmartMedBox Caregiver Dashboard</h1>
        <p class="subtle">Today: {summary.get("total", 0)} logged events</p>
      </div>
      <p class="subtle">Auto-refreshes every 30 seconds</p>
    </header>
    <div class="summary">
      {_metric("Taken", summary.get("taken", 0))}
      {_metric("Late", summary.get("late", 0))}
      {_metric("Missed", summary.get("missed", 0))}
      {_metric("Double", summary.get("double", 0))}
      {_metric("Alerts", summary.get("alerts", 0))}
    </div>
    <section>
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Dose</th>
            <th>Outcome</th>
            <th>Overdue</th>
            <th>Alert</th>
            <th>Message</th>
          </tr>
        </thead>
        <tbody>
          {rows}
        </tbody>
      </table>
    </section>
  </main>
</body>
</html>"""


def _metric(label: str, value: int) -> str:
    return f"<div class=\"metric\"><span>{escape(label)}</span><strong>{value}</strong></div>"


def _render_event_row(event: Dict) -> str:
    action = escape(str(event.get("action") or "idle"))
    label = escape(str(event.get("label") or f"Compartment {event.get('compartment', '')}"))
    message = escape(str(event.get("message") or ""))
    ts = escape(str(event.get("ts") or ""))
    overdue = int(event.get("minutes_overdue") or 0)
    notified = "Yes" if event.get("notified") else "No"

    return f"""
<tr>
  <td>{ts}</td>
  <td>{label}</td>
  <td><span class="tag {action}">{action}</span></td>
  <td>{overdue} min</td>
  <td>{notified}</td>
  <td>{message}</td>
</tr>"""


class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP handler that renders the dashboard from the configured store."""

    store_path = Config.SMARTMEDBOX_DB

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path not in ("/", "/index.html"):
            self.send_error(404)
            return

        store = AdherenceStore(self.store_path)
        html = render_dashboard(store.summary_today(), store.recent_events())
        body = html.encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        return None


def run_dashboard(host: str = "127.0.0.1", port: int = 8000, db_path: str = Config.SMARTMEDBOX_DB) -> None:
    DashboardHandler.store_path = db_path
    server = ThreadingHTTPServer((host, port), DashboardHandler)
    print(f"SmartMedBox caregiver dashboard: http://{host}:{port}")
    server.serve_forever()


def main() -> None:
    parser = ArgumentParser(description="Run the SmartMedBox caregiver dashboard.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--db", default=Config.SMARTMEDBOX_DB)
    args = parser.parse_args()

    run_dashboard(host=args.host, port=args.port, db_path=args.db)


if __name__ == "__main__":
    main()
