# app/routes/discovery.py

from typing import Dict, List, Any
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import psycopg2
import json

from app.agents.discovery_agent import suggest_accounts_for_brand

router = APIRouter(prefix="/discovery", tags=["discovery"])


def _get_db_conn():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="asa",
        user="postgres",
        password="postgres",
    )


def _get_existing_handles_for_brand(brand_id: str) -> dict:
    """
    Collect existing handles for the brand itself (brands.account_handles)
    AND any already-approved sources from the sources table.
    Returns a dict:
      {
        "instagram": [...],
        "facebook": [...],
        "linkedin": [...]
      }
    """
    conn = _get_db_conn()
    cur = conn.cursor()

    # Brand's own handles
    cur.execute(
        """
        select account_handles
        from brands
        where id = %s
        """,
        (brand_id,),
    )
    row = cur.fetchone()
    if row:
        account_handles = row[0]
    else:
        account_handles = {}

    if isinstance(account_handles, str):
        account_handles = json.loads(account_handles)

    existing = {
        "instagram": [],
        "facebook": [],
        "linkedin": [],
    }

    for plat in existing.keys():
        handle = account_handles.get(plat)
        if handle:
            existing[plat].append(handle)

    # Now pull all sources
    cur.execute(
        """
        select platform, handle
        from sources
        """
    )
    for platform, handle in cur.fetchall():
        platform = (platform or "").lower()
        if platform in existing and handle:
            existing[platform].append(handle)

    cur.close()
    conn.close()
    return existing


@router.get("/suggestions")
def get_suggestions(max_suggestions: int = 15) -> Dict[str, List[Dict[str, Any]]]:
    """
    Return suggested accounts for the FuelAI brand as JSON.
    """
    brand_id = "4c91c352-66f0-4c50-8466-dbaf4dfbff04"

    conn = _get_db_conn()
    cur = conn.cursor()
    cur.execute(
        """
        select name
        from brands
        where id = %s
        """,
        (brand_id,),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return {"suggestions": []}

    brand_name = row[0]
    existing_handles = _get_existing_handles_for_brand(brand_id)

    brand_description = (
        "AI that runs outbound and follow-ups for sales teams, acting like a human SDR "
        "that never gets tired. It plugs into existing workflows and keeps reps in more "
        "conversations instead of admin hell."
    )

    target_audience = (
        "B2B SaaS founders, sales leaders, SDR/BDR managers, and RevOps leaders who care "
        "about pipeline, outbound efficiency, and scaling without just hiring more headcount."
    )

    suggestions = suggest_accounts_for_brand(
        brand_name=brand_name,
        brand_description=brand_description,
        target_audience=target_audience,
        existing_handles=existing_handles,
        max_suggestions=max_suggestions,
    )

    return {"suggestions": suggestions}


@router.get("/ui", response_class=HTMLResponse)
def discovery_ui():
    """
    Simple HTML UI to view suggested accounts and approve them.
    Now loads instantly and fetches suggestions asynchronously.
    """
    brand_id = "4c91c352-66f0-4c50-8466-dbaf4dfbff04"

    conn = _get_db_conn()
    cur = conn.cursor()
    cur.execute(
        """
        select name
        from brands
        where id = %s
        """,
        (brand_id,),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return HTMLResponse("<h1>No brand found</h1>")

    brand_name = row[0]

    # Don't fetch suggestions here - do it async via JavaScript for instant page load
    rows_html = """
    <tr id="loading-row">
        <td colspan="8" style="text-align:center; padding:40px;">
            <div class="loading-spinner"></div>
            <div style="margin-top:16px; color:#6b7280;">
                🤖 AI is analyzing your audience and finding relevant accounts...<br>
                <small>This takes 5-10 seconds</small>
            </div>
        </td>
    </tr>
    """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <title>Discovery Suggestions</title>
      <meta charset="utf-8" />
      <style>
        :root {{
          --brand-blue: #01CAFD;
          --bg-light: #f5f7fb;
          --border-subtle: #e1e4ea;
          --text-main: #1f2933;
          --text-muted: #6b7280;
        }}
        * {{
          box-sizing: border-box;
        }}
        body {{
          font-family: -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
          padding: 24px;
          margin: 0;
          background: var(--bg-light);
          color: var(--text-main);
        }}
        .shell {{
          max-width: 1080px;
          margin: 0 auto;
          background: white;
          border-radius: 12px;
          padding: 20px 24px 28px;
          box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
          border: 1px solid var(--border-subtle);
        }}
        h1 {{
          margin: 0 0 4px 0;
          font-size: 22px;
        }}
        .subhead {{
          margin: 0 0 16px 0;
          font-size: 14px;
          color: var(--text-muted);
        }}
        table {{
          border-collapse: collapse;
          width: 100%;
          margin-top: 8px;
        }}
        th, td {{
          border-bottom: 1px solid var(--border-subtle);
          padding: 8px 10px;
          vertical-align: top;
          font-size: 13px;
        }}
        th {{
          background: #f9fafb;
          text-align: left;
          font-weight: 600;
          font-size: 12px;
          letter-spacing: 0.03em;
          text-transform: uppercase;
          color: #6b7280;
        }}
        tr:nth-child(even) td {{
          background: #fbfcff;
        }}
        tr.approved td {{
          background: #e6ffed !important;
        }}
        .badge {{
          display: inline-block;
          padding: 2px 7px;
          border-radius: 999px;
          font-size: 11px;
          font-weight: 500;
        }}
        .badge-ig {{
          background: rgba(237, 100, 166, 0.12);
          color: #be185d;
        }}
        .badge-fb {{
          background: rgba(37, 99, 235, 0.12);
          color: #1d4ed8;
        }}
        .badge-li {{
          background: rgba(14, 116, 144, 0.12);
          color: #0f766e;
        }}
        .type-pill {{
          padding: 2px 8px;
          border-radius: 999px;
          font-size: 11px;
          border: 1px solid var(--border-subtle);
          color: var(--text-muted);
        }}
        .fit-score {{
          font-variant-numeric: tabular-nums;
        }}
        .voice-notes {{
          margin-top: 4px;
          font-size: 11px;
          color: var(--text-muted);
        }}
        button {{
          padding: 4px 10px;
          border-radius: 999px;
          border: none;
          background: var(--brand-blue);
          color: #02243a;
          font-size: 12px;
          font-weight: 600;
          cursor: pointer;
        }}
        button[disabled] {{
          background: #d1d5db;
          color: #4b5563;
          cursor: default;
        }}
        .header-row {{
          display: flex;
          justify-content: space-between;
          align-items: baseline;
          margin-bottom: 12px;
        }}
        .refresh-hint {{
          font-size: 11px;
          color: var(--text-muted);
        }}
        .loading-spinner {{
          width: 40px;
          height: 40px;
          margin: 0 auto;
          border: 4px solid var(--border-subtle);
          border-top-color: var(--brand-blue);
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }}
        @keyframes spin {{
          to {{ transform: rotate(360deg); }}
        }}
      </style>
      <script>
        // Load suggestions asynchronously when page loads
        async function loadSuggestions() {{
          try {{
            const resp = await fetch("/discovery/suggestions?max_suggestions=15");
            
            if (!resp.ok) {{
              throw new Error("Failed to fetch suggestions");
            }}
            
            const data = await resp.json();
            const suggestions = data.suggestions || [];
            
            const tbody = document.querySelector("tbody");
            
            if (suggestions.length === 0) {{
              tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:40px;color:#6b7280;">No suggestions found. Try again later.</td></tr>';
              return;
            }}
            
            // Build table rows
            let html = '';
            suggestions.forEach((s, idx) => {{
              const i = idx + 1;
              let platBadge = '';
              if (s.platform === 'instagram') {{
                platBadge = '<span class="badge badge-ig">Instagram</span>';
              }} else if (s.platform === 'facebook') {{
                platBadge = '<span class="badge badge-fb">Facebook</span>';
              }} else {{
                platBadge = '<span class="badge badge-li">LinkedIn</span>';
              }}
              
              const typeLabel = (s.type || 'inspiration').charAt(0).toUpperCase() + (s.type || 'inspiration').slice(1);
              const fitScore = Math.round(s.fit_score || 0);
              
              let reasonCell = s.reason || '';
              if (s.voice_notes) {{
                reasonCell += '<div class="voice-notes"><strong>Voice to borrow:</strong> ' + s.voice_notes + '</div>';
              }}
              
              const isCompetitor = s.type === 'competitor' ? 'true' : 'false';
              
              html += `
                <tr id="row-${{i}}">
                  <td>${{i}}</td>
                  <td>${{platBadge}}</td>
                  <td>${{s.handle}}</td>
                  <td>${{s.display_name || ''}}</td>
                  <td><span class="type-pill">${{typeLabel}}</span></td>
                  <td class="fit-score">${{fitScore}}%</td>
                  <td>${{reasonCell}}</td>
                  <td>
                    <button onclick="approve('${{s.platform}}', '${{s.handle}}', ${{isCompetitor}}, 'row-${{i}}')">
                      Approve
                    </button>
                  </td>
                </tr>
              `;
            }});
            
            tbody.innerHTML = html;
            
          }} catch (err) {{
            console.error(err);
            document.querySelector("tbody").innerHTML = 
              '<tr><td colspan="8" style="text-align:center;padding:40px;color:#ef4444;">Error loading suggestions. Please refresh the page.</td></tr>';
          }}
        }}
        
        async function approve(platform, handle, isCompetitor, rowId) {{
          const payload = {{
            platform: platform,
            handle: handle,
            is_competitor: isCompetitor,
            fetch_schedule: "daily"
          }};

          try {{
            const resp = await fetch("/sources", {{
              method: "POST",
              headers: {{
                "Content-Type": "application/json"
              }},
              body: JSON.stringify(payload)
            }});

            if (!resp.ok) {{
              alert("Error approving: " + resp.status);
              return;
            }}

            const data = await resp.json();
            console.log("Approved:", data);

            const row = document.getElementById(rowId);
            if (row) {{
              row.classList.add("approved");
              const btn = row.querySelector("button");
              if (btn) {{
                btn.disabled = true;
                btn.innerText = "Approved";
              }}
            }}
          }} catch (err) {{
            console.error(err);
            alert("Network error approving source");
          }}
        }}
        
        // Load suggestions when page loads
        window.addEventListener('DOMContentLoaded', loadSuggestions);
      </script>
    </head>
    <body>
      <div class="shell">
        <div class="header-row">
          <div>
            <h1>Discovery Suggestions for {brand_name}</h1>
            <p class="subhead">
              AI-recommended accounts your ICP likely follows. Click <strong>Approve</strong> to start tracking them.
            </p>
          </div>
          <div class="refresh-hint">
            Refresh this page to get a fresh batch of suggestions.
          </div>
        </div>
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Platform</th>
              <th>Handle</th>
              <th>Display Name</th>
              <th>Type</th>
              <th>Fit</th>
              <th>Reason &amp; Voice</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {rows_html}
          </tbody>
        </table>
      </div>
    </body>
    </html>
    """

    return HTMLResponse(html)