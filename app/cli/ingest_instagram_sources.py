# app/cli/ingest_instagram_sources.py

from typing import List, Tuple

import psycopg2

from app.services.ingestion_service import upsert_posts
from app.services.instagram_scraper import fetch_instagram_posts


def _get_db_conn():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="asa",
        user="postgres",
        password="postgres",
    )


def get_instagram_sources() -> List[Tuple[str, str]]:
    """
    Return a list of (source_id, handle) for all instagram sources
    that we should fetch for. (You can filter on fetch_schedule later.)
    """
    conn = _get_db_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, handle
        FROM sources
        WHERE platform = 'instagram'
        """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [(str(r[0]), r[1]) for r in rows]


def main(limit: int = 20):
    sources = get_instagram_sources()
    if not sources:
        print("No instagram sources found in the database.")
        return

    print(f"Found {len(sources)} instagram sources.")
    for source_id, handle in sources:
        print(f"\n=== Fetching posts for @{handle} ===")
        posts = fetch_instagram_posts(handle, limit=limit)
        print(f"Fetched {len(posts)} posts from Apify for @{handle}")

        if not posts:
            continue

        upsert_posts(
            platform="instagram",
            source_id=source_id,
            posts=posts,
        )
        print(f"Upserted posts into posts_raw for @{handle}")


if __name__ == "__main__":
    main()