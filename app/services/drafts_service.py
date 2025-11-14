# app/services/drafts_service.py

from typing import Dict, Any, List

from app.db.connection import get_db_cursor


def save_draft(brand_id: str, package: Dict[str, Any]) -> List[str]:
    """
    Save a generated post package into the drafts table.

    We create ONE draft row per platform (instagram, facebook, linkedin),
    using the schema:

      - brand_id   (uuid)
      - platform   (text)
      - type       (text)     -> style, e.g. 'educational', 'meme', 'sales'
      - caption    (text)
      - hashtags   (text[])
      - asset_refs (text[])   -> empty for now
      - status     (text)     -> defaults to 'draft'

    Returns a list of the created draft IDs (as strings).
    """
    created_ids: List[str] = []

    core = package.get("core", {})
    core_style = core.get("style", "unspecified")

    with get_db_cursor() as cur:
        for platform in ("instagram", "facebook", "linkedin"):
            section = package.get(platform, {}) or {}

            caption = section.get("caption", "")
            hashtags = section.get("hashtags", []) or []
            style = section.get("style") or core_style or "unspecified"

            # Ensure hashtags is a Python list of strings
            if not isinstance(hashtags, list):
                hashtags = [str(hashtags)]

            cur.execute(
                """
                insert into drafts (
                  brand_id,
                  platform,
                  type,
                  caption,
                  hashtags,
                  asset_refs
                )
                values (%s, %s, %s, %s, %s, %s)
                returning id
                """,
                (
                    brand_id,
                    platform,
                    style,
                    caption,
                    hashtags,   # psycopg2 will adapt Python list -> text[]
                    [],         # asset_refs empty for now
                ),
            )

            draft_id = cur.fetchone()[0]
            created_ids.append(str(draft_id))

    return created_ids