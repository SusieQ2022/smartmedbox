"""Unit tests for dashboard rendering."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dashboard import render_dashboard  # noqa: E402


def test_render_dashboard_includes_summary_counts():
    html = render_dashboard(
        {
            "taken": 2,
            "late": 1,
            "missed": 0,
            "double": 0,
            "alerts": 1,
            "total": 4,
        },
        [],
    )

    assert "SmartMedBox Caregiver Dashboard" in html
    assert "Today: 4 logged events" in html
    assert "<strong>2</strong>" in html
    assert "No adherence events yet." in html


def test_render_dashboard_escapes_event_message():
    html = render_dashboard(
        {"taken": 0, "late": 0, "missed": 1, "double": 0, "alerts": 1, "total": 1},
        [
            {
                "ts": "2026-06-30T08:35:00",
                "compartment": 1,
                "label": "Noon",
                "action": "alert_caregiver",
                "minutes_overdue": 35,
                "notified": 1,
                "message": "<script>alert('x')</script>",
            }
        ],
    )

    assert "&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt;" in html
    assert "<script>" not in html
