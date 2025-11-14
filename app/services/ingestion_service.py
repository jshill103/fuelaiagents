# app/services/ingestion_service.py

from typing import Any, Dict, List, Optional
from datetime import datetime
import json

from app.db.connection import get_db_cursor


def _parse_iso_datetime(value: Any) -> Optional[datetime]:
    """
    Best-effort parse of an ISO timestamp string.
    Returns a datetime or None if we can't parse it.
    """
    if not value:
        return None

    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        # Allow strings like "2025-11-13T16:45:00Z"
        try:
            # replace trailing Z with +00:00 for fromisoformat
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            return None

    return None


def upsert_posts(
    platform: str,
    source_id: str,
    posts: List[Dict[str, Any]],
) -> None:
    """
    Insert a batch of normalized posts into posts_raw.

    This function is PLATFORM-AGNOSTIC. It doesn't care if the data came
    from Instagram, Facebook, or LinkedIn — as long as each item in `posts`
    has the expected keys.

    Expected shape for each `post` in `posts`:

      {
        "post_id": str,            # required, platform-native ID or slug
        "caption": str,            # full text / body; can be empty
        "hashtags": [str, ...],    # optional list of hashtags, without '#'
        "media_urls": [str, ...],  # optional list of image/video URLs
        "posted_at": str | datetime | None,  # ISO string or datetime
        "engagement": {            # json-serializable dict, optional
            "likes": int,
            "comments": int,
            "shares": int,
            ...
        }
      }

    It will:
      - parse posted_at if it's a string
      - ensure hashtags/media_urls are lists of strings
      - JSON-encode engagement into the jsonb column
    """
    if not posts:
        return

    with get_db_cursor() as cur:
        for post in posts:
            post_id = str(post.get("post_id") or "").strip()
            if not post_id:
                # no usable ID, skip this entry
                continue

            caption = post.get("caption") or ""

            # Normalize hashtags to a list[str]
            hashtags = post.get("hashtags") or []
            if isinstance(hashtags, str):
                # if someone passes "#a #b #c" as a string, split on whitespace
                hashtags = [h.lstrip("#") for h in hashtags.split() if h.strip()]
            elif isinstance(hashtags, list):
                hashtags = [str(h).lstrip("#") for h in hashtags]
            else:
                hashtags = []

            # Normalize media_urls to a list[str]
            media_urls = post.get("media_urls") or []
            if isinstance(media_urls, str):
                media_urls = [media_urls]
            elif isinstance(media_urls, list):
                media_urls = [str(u) for u in media_urls]
            else:
                media_urls = []

            posted_at = _parse_iso_datetime(post.get("posted_at"))

            engagement = post.get("engagement") or {}
            if not isinstance(engagement, dict):
                engagement = {}

            # Insert into posts_raw using only existing columns
            cur.execute(
                """
                INSERT INTO posts_raw (
                    source_id,
                    platform,
                    post_id,
                    caption,
                    hashtags,
                    media_urls,
                    posted_at,
                    engagement
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (source_id, platform, post_id) DO NOTHING
                """,
                (
                    source_id,
                    platform,
                    post_id,
                    caption,
                    hashtags,
                    media_urls,
                    posted_at,
                    json.dumps(engagement),
                ),
            )