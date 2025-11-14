# app/services/instagram_scraper.py

from typing import Any, Dict, List, Optional
import os
import json
from datetime import datetime, timezone

import httpx


def _get_apify_token() -> str:
    """
    Read the Apify token from the environment.
    """
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        raise RuntimeError("APIFY_TOKEN not set in environment")
    return token


def _get_ig_session_cookie() -> Optional[str]:
    """
    Read the Instagram session cookie from the environment.

    Supports both:
      IG_SESSIONID=...
      IG_SESSION_COOKIE=...

    Use the one you already have in .env (IG_SESSIONID).
    """
    return os.environ.get("IG_SESSIONID") or os.environ.get("IG_SESSION_COOKIE")


def _epoch_to_iso(ts: Any) -> Optional[str]:
    """
    Convert an epoch timestamp to an ISO8601 string in UTC, if possible.
    Otherwise, return None.
    """
    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    return None


def fetch_instagram_posts(handle: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Fetch the latest posts for a given Instagram handle using Apify's instagram-scraper.

    Input:
        handle: Instagram username (with or without leading '@')
        limit:  how many recent posts to request

    Returns:
        A list of *normalized* posts in the shape expected by ingestion_service.upsert_posts:

        {
          "post_id": str,
          "caption": str,
          "hashtags": [str],
          "media_urls": [str],
          "posted_at": str | None,      # ISO8601 string if known
          "engagement": {
              "likes": int,
              "comments": int,
              ... (other fields can be added later)
          }
        }
    """
    token = _get_apify_token()
    username = handle.lstrip("@")  # make sure we don't send '@@something' to Apify

    url = (
        "https://api.apify.com/v2/acts/"
        "apify~instagram-scraper/run-sync-get-dataset-items"
        f"?token={token}"
    )

    payload: Dict[str, Any] = {
        "usernames": [username],
        "resultsLimit": limit,
        "includeStories": False,
        "searchType": "user",
        "addParentData": True,
    }

    session_cookie = _get_ig_session_cookie()
    if session_cookie:
        # Most IG actors on Apify accept this field name; adjust if your actor
        # uses something different (check its docs).
        payload["sessionCookie"] = session_cookie

    print(f"[instagram_scraper] Fetching IG posts for @{username} (limit={limit})")
    resp = httpx.post(url, json=payload, timeout=60)
    print("[instagram_scraper] HTTP status:", resp.status_code)

    # Apify commonly returns 201 = "run created + dataset items ready"
    if resp.status_code not in (200, 201):
        print("[instagram_scraper] Non-200/201 response body (truncated):")
        print(resp.text[:300])
        return []

    try:
        items = resp.json()
    except json.JSONDecodeError:
        print("[instagram_scraper] JSON decode error, raw (truncated):")
        print(resp.text[:500])
        return []

    # Actor-level error (what you've been seeing: {"error":"no_items", ...})
    if isinstance(items, list) and items and isinstance(items[0], dict) and "error" in items[0]:
        print("[instagram_scraper] Apify error object:", items[0])
        return []

    normalized: List[Dict[str, Any]] = []

    for item in items:
        # Apify field names can vary; this is a best-effort mapping.
        post_id = item.get("id") or item.get("shortCode") or item.get("url")
        if not post_id:
            continue

        caption = (
            item.get("caption")
            or item.get("captionText")
            or ""
        )

        # Extract hashtags from caption
        hashtags: List[str] = []
        if caption:
            for word in caption.split():
                if word.startswith("#") and len(word) > 1:
                    hashtags.append(word.lstrip("#"))

        # Media URLs: resources[] or main url/displayUrl
        media_urls: List[str] = []
        resources = item.get("resources") or item.get("images") or []
        if isinstance(resources, list):
            for r in resources:
                if not isinstance(r, dict):
                    continue
                url_field = r.get("url") or r.get("src")
                if url_field:
                    media_urls.append(url_field)

        main_url = item.get("url") or item.get("displayUrl")
        if main_url and main_url not in media_urls:
            media_urls.append(main_url)

        # Timestamp: "timestamp" or "takenAtTimestamp"
        ts = item.get("timestamp") or item.get("takenAtTimestamp")
        ts_iso = _epoch_to_iso(ts) if isinstance(ts, (int, float)) else ts
        # At this point ts_iso may be a string or None; ingestion will try to parse

        # Engagement fields
        likes = (
            item.get("likesCount")
            or item.get("likes")
            or (item.get("edge_liked_by") or {}).get("count")
        )
        comments = (
            item.get("commentsCount")
            or item.get("comments")
            or (item.get("edge_media_to_comment") or {}).get("count")
        )

        engagement = {
            "likes": int(likes or 0),
            "comments": int(comments or 0),
        }

        normalized.append(
            {
                "post_id": str(post_id),
                "caption": caption or "",
                "hashtags": hashtags,
                "media_urls": media_urls,
                "posted_at": ts_iso,
                "engagement": engagement,
            }
        )

    print(f"[instagram_scraper] Normalized {len(normalized)} posts for @{username}")
    return normalized