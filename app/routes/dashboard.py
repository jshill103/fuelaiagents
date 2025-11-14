# app/routes/dashboard.py

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
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


@router.get("/", response_class=HTMLResponse)
def dashboard_home():
    """
    Main dashboard showing all sources, stats, and scheduled posts.
    """
    conn = _get_db_conn()
    cur = conn.cursor()
    
    # Get all sources with post counts
    cur.execute("""
        SELECT 
            s.id,
            s.platform,
            s.handle,
            s.is_competitor,
            s.fetch_schedule,
            s.last_crawl_at,
            COUNT(DISTINCT p.id) as post_count,
            MAX(p.posted_at) as latest_post,
            SUM((p.engagement->>'likes')::int) as total_likes,
            SUM((p.engagement->>'comments')::int) as total_comments
        FROM sources s
        LEFT JOIN posts_raw p ON p.source_id = s.id
        GROUP BY s.id, s.platform, s.handle, s.is_competitor, s.fetch_schedule, s.last_crawl_at
        ORDER BY post_count DESC, s.handle
    """)
    sources = cur.fetchall()
    
    # Get draft/scheduled posts count
    cur.execute("""
        SELECT 
            platform,
            status,
            COUNT(*) as count
        FROM drafts
        GROUP BY platform, status
        ORDER BY platform, status
    """)
    draft_stats = cur.fetchall()
    
    # Get total stats
    cur.execute("SELECT COUNT(*) FROM sources")
    total_sources = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM posts_raw")
    total_posts = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM drafts WHERE status = 'draft'")
    pending_drafts = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM drafts WHERE scheduled_at IS NOT NULL AND scheduled_at > NOW()")
    scheduled_posts = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    # Build sources table
    sources_html = ""
    if sources:
        for (src_id, platform, handle, is_competitor, schedule, last_crawl, 
             post_count, latest_post, total_likes, total_comments) in sources:
            
            platform_badge = _get_platform_badge(platform)
            type_badge = '<span class="badge badge-competitor">Competitor</span>' if is_competitor else '<span class="badge badge-inspiration">Inspiration</span>'
            
            # Format stats
            likes_str = f"{total_likes:,}" if total_likes else "0"
            comments_str = f"{total_comments:,}" if total_comments else "0"
            
            # Last crawl
            if last_crawl:
                last_crawl_str = _format_time_ago(last_crawl)
            else:
                last_crawl_str = "Never"
            
            # Latest post
            if latest_post:
                latest_post_str = _format_time_ago(latest_post)
            else:
                latest_post_str = "N/A"
            
            sources_html += f"""
            <tr>
                <td>{platform_badge}</td>
                <td><a href="https://instagram.com/{handle}" target="_blank">@{handle}</a></td>
                <td>{type_badge}</td>
                <td>{post_count}</td>
                <td>{likes_str}</td>
                <td>{comments_str}</td>
                <td>{latest_post_str}</td>
                <td>{last_crawl_str}</td>
                <td><span class="schedule-badge">{schedule}</span></td>
                <td>
                    <button class="btn-small btn-fetch" onclick="fetchPosts('{src_id}', '{handle}')">Fetch</button>
                    <button class="btn-small btn-delete" onclick="deleteSource('{src_id}', '{handle}')">Delete</button>
                </td>
            </tr>
            """
    else:
        sources_html = '<tr><td colspan="10" style="text-align:center;color:#6b7280;">No sources added yet. Use Discovery to find accounts!</td></tr>'
    
    # Build draft stats
    draft_stats_html = ""
    for platform, status, count in draft_stats:
        draft_stats_html += f"""
        <div class="stat-item">
            <div class="stat-label">{platform.title()} - {status.title()}</div>
            <div class="stat-value">{count}</div>
        </div>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FuelAI Agents Dashboard</title>
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
                --success: #10b981;
                --warning: #f59e0b;
                --danger: #ef4444;
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
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
                gap: 16px;
                margin-bottom: 24px;
            }}
            .stat-card {{
                background: white;
                border-radius: 12px;
                padding: 20px;
                border: 1px solid var(--border-subtle);
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }}
            .stat-label {{
                font-size: 13px;
                font-weight: 500;
                color: var(--text-muted);
                text-transform: uppercase;
                letter-spacing: 0.03em;
                margin-bottom: 8px;
            }}
            .stat-value {{
                font-size: 32px;
                font-weight: 700;
                color: var(--text-main);
            }}
            .stat-change {{
                font-size: 12px;
                color: var(--success);
                margin-top: 4px;
            }}
            .panel {{
                background: white;
                border-radius: 12px;
                padding: 24px;
                border: 1px solid var(--border-subtle);
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                margin-bottom: 24px;
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
            .btn {{
                padding: 8px 16px;
                border-radius: 6px;
                border: none;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s;
                text-decoration: none;
                display: inline-block;
            }}
            .btn-primary {{
                background: var(--brand-blue);
                color: var(--brand-dark);
            }}
            .btn-primary:hover {{
                filter: brightness(1.1);
            }}
            .btn-small {{
                padding: 4px 10px;
                font-size: 12px;
                border-radius: 4px;
                margin-right: 4px;
            }}
            .btn-fetch {{
                background: #10b981;
                color: white;
            }}
            .btn-delete {{
                background: #ef4444;
                color: white;
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
            .badge-competitor {{
                background: rgba(239, 68, 68, 0.12);
                color: #dc2626;
            }}
            .badge-inspiration {{
                background: rgba(16, 185, 129, 0.12);
                color: #059669;
            }}
            .schedule-badge {{
                background: rgba(59, 130, 246, 0.12);
                color: #2563eb;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 11px;
            }}
            a {{
                color: var(--brand-blue);
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            .empty-state {{
                text-align: center;
                padding: 60px 20px;
                color: var(--text-muted);
            }}
            .loading {{
                display: inline-block;
                width: 16px;
                height: 16px;
                border: 2px solid var(--border-subtle);
                border-top-color: var(--brand-blue);
                border-radius: 50%;
                animation: spin 0.6s linear infinite;
            }}
            @keyframes spin {{
                to {{ transform: rotate(360deg); }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <div class="logo">⚡ FuelAI Agents</div>
                <nav class="nav">
                    <a href="/dashboard" class="active">Dashboard</a>
                    <a href="/discovery/ui">Discover</a>
                    <a href="/dashboard/scheduled">Scheduled</a>
                    <a href="/docs">API</a>
                </nav>
            </div>
        </div>
        
        <div class="container">
            <!-- Stats Overview -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Total Sources</div>
                    <div class="stat-value">{total_sources}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Posts Ingested</div>
                    <div class="stat-value">{total_posts:,}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Pending Drafts</div>
                    <div class="stat-value">{pending_drafts}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Scheduled Posts</div>
                    <div class="stat-value">{scheduled_posts}</div>
                </div>
            </div>
            
            <!-- Sources Table -->
            <div class="panel">
                <div class="panel-header">
                    <h2 class="panel-title">Tracked Accounts</h2>
                    <div>
                        <a href="/discovery/ui" class="btn btn-primary">+ Discover New Accounts</a>
                        <button class="btn btn-primary" onclick="showAddSourceModal()">+ Add Manual</button>
                    </div>
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>Platform</th>
                            <th>Handle</th>
                            <th>Type</th>
                            <th>Posts</th>
                            <th>Total Likes</th>
                            <th>Total Comments</th>
                            <th>Latest Post</th>
                            <th>Last Crawl</th>
                            <th>Schedule</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sources_html}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Add Source Modal -->
        <div id="addSourceModal" style="display:none; position:fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.5); z-index:1000; padding:40px;">
            <div style="max-width:500px; margin:0 auto; background:white; border-radius:12px; padding:32px;">
                <h3 style="margin:0 0 20px 0;">Add New Source</h3>
                <form id="addSourceForm">
                    <div style="margin-bottom:16px;">
                        <label style="display:block; margin-bottom:4px; font-size:13px; font-weight:500;">Platform</label>
                        <select id="platform" style="width:100%; padding:8px; border:1px solid var(--border-subtle); border-radius:6px;">
                            <option value="instagram">Instagram</option>
                            <option value="facebook">Facebook</option>
                            <option value="linkedin">LinkedIn</option>
                        </select>
                    </div>
                    <div style="margin-bottom:16px;">
                        <label style="display:block; margin-bottom:4px; font-size:13px; font-weight:500;">Handle (without @)</label>
                        <input type="text" id="handle" placeholder="nike" style="width:100%; padding:8px; border:1px solid var(--border-subtle); border-radius:6px;">
                    </div>
                    <div style="margin-bottom:16px;">
                        <label style="display:flex; align-items:center; gap:8px;">
                            <input type="checkbox" id="is_competitor">
                            <span style="font-size:13px;">Mark as competitor</span>
                        </label>
                    </div>
                    <div style="display:flex; gap:8px; justify-content:flex-end;">
                        <button type="button" onclick="hideAddSourceModal()" class="btn" style="background:#e5e7eb; color:#374151;">Cancel</button>
                        <button type="submit" class="btn btn-primary">Add Source</button>
                    </div>
                </form>
            </div>
        </div>
        
        <script>
            function showAddSourceModal() {{
                document.getElementById('addSourceModal').style.display = 'block';
            }}
            
            function hideAddSourceModal() {{
                document.getElementById('addSourceModal').style.display = 'none';
                document.getElementById('addSourceForm').reset();
            }}
            
            document.getElementById('addSourceForm').addEventListener('submit', async (e) => {{
                e.preventDefault();
                const platform = document.getElementById('platform').value;
                const handle = document.getElementById('handle').value.trim();
                const is_competitor = document.getElementById('is_competitor').checked;
                
                if (!handle) {{
                    alert('Please enter a handle');
                    return;
                }}
                
                try {{
                    const resp = await fetch('/sources', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            platform,
                            handle,
                            is_competitor,
                            fetch_schedule: 'daily'
                        }})
                    }});
                    
                    if (resp.ok) {{
                        hideAddSourceModal();
                        location.reload();
                    }} else {{
                        alert('Error adding source');
                    }}
                }} catch (err) {{
                    alert('Network error: ' + err.message);
                }}
            }});
            
            async function fetchPosts(sourceId, handle) {{
                if (!confirm(`Fetch latest posts for @${{handle}}?`)) return;
                
                alert('Fetching posts... This may take 1-2 minutes.');
                
                try {{
                    const resp = await fetch(`/dashboard/fetch/${{sourceId}}`, {{ method: 'POST' }});
                    const data = await resp.json();
                    
                    if (resp.ok) {{
                        alert(`Success! Fetched ${{data.posts_fetched}} posts for @${{handle}}`);
                        location.reload();
                    }} else {{
                        alert('Error: ' + (data.error || 'Unknown error'));
                    }}
                }} catch (err) {{
                    alert('Network error: ' + err.message);
                }}
            }}
            
            async function deleteSource(sourceId, handle) {{
                if (!confirm(`Delete @${{handle}}? This will also delete all ingested posts.`)) return;
                
                try {{
                    const resp = await fetch(`/sources/${{sourceId}}`, {{ method: 'DELETE' }});
                    
                    if (resp.ok) {{
                        alert(`Deleted @${{handle}}`);
                        location.reload();
                    }} else {{
                        alert('Error deleting source');
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


@router.post("/fetch/{source_id}")
async def fetch_source_posts(source_id: str):
    """
    Manually trigger a fetch for a specific source.
    """
    from app.services.instagram_scraper import fetch_instagram_posts
    from app.services.ingestion_service import upsert_posts
    
    conn = _get_db_conn()
    cur = conn.cursor()
    
    # Get source details
    cur.execute("""
        SELECT platform, handle
        FROM sources
        WHERE id = %s
    """, (source_id,))
    
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Source not found")
    
    platform, handle = row
    
    if platform != "instagram":
        raise HTTPException(status_code=400, detail="Only Instagram supported for now")
    
    try:
        # Fetch posts
        posts = fetch_instagram_posts(handle, limit=20)
        
        # Ingest
        upsert_posts(
            platform=platform,
            source_id=source_id,
            posts=posts
        )
        
        # Update last_crawl_at
        cur.execute("""
            UPDATE sources
            SET last_crawl_at = NOW()
            WHERE id = %s
        """, (source_id,))
        conn.commit()
        
        cur.close()
        conn.close()
        
        return {
            "success": True,
            "posts_fetched": len(posts),
            "handle": handle
        }
        
    except Exception as e:
        cur.close()
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))


def _get_platform_badge(platform: str) -> str:
    """Generate platform badge HTML."""
    badges = {
        "instagram": '<span class="badge badge-ig">Instagram</span>',
        "facebook": '<span class="badge badge-fb">Facebook</span>',
        "linkedin": '<span class="badge badge-li">LinkedIn</span>',
    }
    return badges.get(platform.lower(), f'<span class="badge">{platform}</span>')


def _format_time_ago(dt) -> str:
    """Format datetime as time ago string."""
    if isinstance(dt, str):
        from dateutil import parser
        dt = parser.parse(dt)
    
    now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
    delta = now - dt
    
    seconds = delta.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        mins = int(seconds / 60)
        return f"{mins}m ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours}h ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days}d ago"
    else:
        weeks = int(seconds / 604800)
        return f"{weeks}w ago"

