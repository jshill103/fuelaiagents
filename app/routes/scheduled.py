# app/routes/scheduled.py

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import psycopg2
from datetime import datetime

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _get_db_conn():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="asa",
        user="postgres",
        password="postgres",
    )


@router.get("/scheduled", response_class=HTMLResponse)
def scheduled_posts_view():
    """
    View all scheduled and draft posts.
    """
    conn = _get_db_conn()
    cur = conn.cursor()
    
    # Get all drafts
    cur.execute("""
        SELECT 
            d.id,
            d.brand_id,
            d.platform,
            d.type,
            d.caption,
            d.hashtags,
            d.status,
            d.scheduled_at,
            b.name as brand_name
        FROM drafts d
        LEFT JOIN brands b ON b.id = d.brand_id
        ORDER BY 
            CASE 
                WHEN d.scheduled_at IS NULL THEN 1
                ELSE 0
            END,
            d.scheduled_at ASC,
            d.platform
    """)
    
    drafts = cur.fetchall()
    cur.close()
    conn.close()
    
    # Build drafts table
    drafts_html = ""
    if drafts:
        for (draft_id, brand_id, platform, post_type, caption, hashtags, 
             status, scheduled_at, brand_name) in drafts:
            
            platform_badge = _get_platform_badge(platform)
            status_badge = _get_status_badge(status)
            
            # Format caption (truncate)
            caption_preview = caption[:100] + "..." if len(caption) > 100 else caption
            
            # Format hashtags
            hashtags_str = " ".join([f"#{tag}" for tag in (hashtags or [])[:5]])
            if len(hashtags or []) > 5:
                hashtags_str += f" +{len(hashtags) - 5} more"
            
            # Format scheduled time
            if scheduled_at:
                scheduled_str = datetime.fromisoformat(str(scheduled_at)).strftime("%b %d, %Y %I:%M %p")
            else:
                scheduled_str = '<span style="color:#6b7280;">Not scheduled</span>'
            
            drafts_html += f"""
            <tr>
                <td>{platform_badge}</td>
                <td><span class="type-badge">{post_type}</span></td>
                <td style="max-width:300px;">{caption_preview}</td>
                <td style="font-size:11px; color:#6b7280;">{hashtags_str}</td>
                <td>{status_badge}</td>
                <td>{scheduled_str}</td>
                <td>
                    <button class="btn-small btn-view" onclick="viewDraft('{draft_id}')">View</button>
                    <button class="btn-small btn-delete" onclick="deleteDraft('{draft_id}')">Delete</button>
                </td>
            </tr>
            """
    else:
        drafts_html = '<tr><td colspan="7" style="text-align:center;color:#6b7280;padding:40px;">No drafts yet. Generate content to see scheduled posts!</td></tr>'
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Scheduled Posts - FuelAI Agents</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            :root {{
                --brand-blue: #01CAFD;
                --brand-dark: #02243a;
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
                padding: 0;
                margin: 0;
                background: var(--bg-light);
                color: var(--text-main);
            }}
            .header {{
                background: white;
                border-bottom: 1px solid var(--border-subtle);
                padding: 16px 24px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }}
            .header-content {{
                max-width: 1400px;
                margin: 0 auto;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .logo {{
                font-size: 20px;
                font-weight: 700;
                color: var(--brand-dark);
            }}
            .nav {{
                display: flex;
                gap: 16px;
            }}
            .nav a {{
                color: var(--text-muted);
                text-decoration: none;
                font-size: 14px;
                font-weight: 500;
                padding: 6px 12px;
                border-radius: 6px;
                transition: all 0.2s;
            }}
            .nav a:hover {{
                background: var(--bg-light);
                color: var(--text-main);
            }}
            .nav a.active {{
                background: var(--brand-blue);
                color: var(--brand-dark);
            }}
            .container {{
                max-width: 1400px;
                margin: 24px auto;
                padding: 0 24px;
            }}
            .panel {{
                background: white;
                border-radius: 12px;
                padding: 24px;
                border: 1px solid var(--border-subtle);
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }}
            .panel-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }}
            .panel-title {{
                font-size: 18px;
                font-weight: 600;
                color: var(--text-main);
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid var(--border-subtle);
                font-size: 13px;
            }}
            th {{
                background: #f9fafb;
                font-weight: 600;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.03em;
                color: var(--text-muted);
            }}
            tr:hover td {{
                background: #fbfcff;
            }}
            .badge {{
                display: inline-block;
                padding: 3px 8px;
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
            .status-draft {{
                background: rgba(59, 130, 246, 0.12);
                color: #2563eb;
            }}
            .status-scheduled {{
                background: rgba(16, 185, 129, 0.12);
                color: #059669;
            }}
            .status-published {{
                background: rgba(107, 114, 128, 0.12);
                color: #374151;
            }}
            .type-badge {{
                background: rgba(249, 115, 22, 0.12);
                color: #ea580c;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 11px;
            }}
            .btn-small {{
                padding: 4px 10px;
                font-size: 12px;
                border-radius: 4px;
                margin-right: 4px;
                border: none;
                cursor: pointer;
                font-weight: 500;
            }}
            .btn-view {{
                background: #3b82f6;
                color: white;
            }}
            .btn-delete {{
                background: #ef4444;
                color: white;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <div class="logo">⚡ FuelAI Agents</div>
                <nav class="nav">
                    <a href="/dashboard">Dashboard</a>
                    <a href="/discovery/ui">Discover</a>
                    <a href="/dashboard/scheduled" class="active">Scheduled</a>
                    <a href="/docs">API</a>
                </nav>
            </div>
        </div>
        
        <div class="container">
            <div class="panel">
                <div class="panel-header">
                    <h2 class="panel-title">Scheduled & Draft Posts</h2>
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>Platform</th>
                            <th>Type</th>
                            <th>Caption</th>
                            <th>Hashtags</th>
                            <th>Status</th>
                            <th>Scheduled</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {drafts_html}
                    </tbody>
                </table>
            </div>
        </div>
        
        <script>
            function viewDraft(draftId) {{
                alert('Draft viewer not yet implemented. Draft ID: ' + draftId);
                // TODO: Show modal with full draft details
            }}
            
            async function deleteDraft(draftId) {{
                if (!confirm('Delete this draft?')) return;
                
                try {{
                    const resp = await fetch(`/dashboard/drafts/${{draftId}}`, {{
                        method: 'DELETE'
                    }});
                    
                    if (resp.ok) {{
                        location.reload();
                    }} else {{
                        alert('Error deleting draft');
                    }}
                }} catch (err) {{
                    alert('Network error: ' + err.message);
                }}
            }}
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(html)


@router.delete("/drafts/{draft_id}")
def delete_draft(draft_id: str):
    """Delete a draft post."""
    conn = _get_db_conn()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM drafts WHERE id = %s", (draft_id,))
    conn.commit()
    
    cur.close()
    conn.close()
    
    return {"success": True}


def _get_platform_badge(platform: str) -> str:
    """Generate platform badge HTML."""
    badges = {
        "instagram": '<span class="badge badge-ig">Instagram</span>',
        "facebook": '<span class="badge badge-fb">Facebook</span>',
        "linkedin": '<span class="badge badge-li">LinkedIn</span>',
    }
    return badges.get(platform.lower(), f'<span class="badge">{platform}</span>')


def _get_status_badge(status: str) -> str:
    """Generate status badge HTML."""
    badges = {
        "draft": '<span class="badge status-draft">Draft</span>',
        "scheduled": '<span class="badge status-scheduled">Scheduled</span>',
        "published": '<span class="badge status-published">Published</span>',
    }
    return badges.get(status.lower(), f'<span class="badge">{status}</span>')

