# app/cli/seed_dummy_posts.py

from datetime import datetime, timezone
from typing import Optional

import psycopg2

from app.services.ingestion_service import upsert_posts


def _get_db_conn():
    """
    Same connection settings as the rest of the app.
    Talks to the Postgres running in Docker (asa_postgres).
    """
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="asa",
        user="postgres",
        password="postgres",
    )


def get_source_id(platform: str, handle: str) -> Optional[str]:
    """
    Look up the sources.id for a given platform + handle combo.
    Returns the UUID as a string, or None if not found.
    """
    conn = _get_db_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id
        FROM sources
        WHERE platform = %s
          AND handle = %s
        LIMIT 1
        """,
        (platform, handle),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return None
    return str(row[0])


def main():
    # For now, let's use the instagram account you just approved: "sdrmemes"
    platform = "instagram"
    handle = "sdrmemes"

    source_id = get_source_id(platform, handle)
    if not source_id:
        print(f"No source found for platform={platform} handle={handle}")
        return

    print(f"Found source_id={source_id} for {platform}:{handle}")

    now = datetime.now(timezone.utc).isoformat()

    # This simulates one scraped SDR meme-style post from that account
    dummy_posts = [
        {
            "post_id": "sdrmemes_demo_001",
            "caption": (
                "When your 'personalized' outbound sequence is really just "
                "the same 3 lines + {{first_name}}.\n\n"
                "If your SDRs are copy/pasting the same DM all day, "
                "you don’t have an SDR problem—you have a system problem."
            ),
            "hashtags": ["sdr", "outbound", "salesmemes"],
            "media_urls": [
                "https://example.com/fake_sdr_meme.png"
            ],
            "posted_at": now,
            "engagement": {
                "likes": 420,
                "comments": 17,
                "shares": 9,
            },
        }
    ]

    upsert_posts(
        platform=platform,
        source_id=source_id,
        posts=dummy_posts,
    )

    print("Inserted 1 dummy post into posts_raw for sdrmemes.")


if __name__ == "__main__":
    main()