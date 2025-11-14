# app/agents/semantic_agent.py

from typing import List, Dict, Any
import os
import math
import psycopg2
from openai import OpenAI


def _get_db_conn():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="asa",
        user="postgres",
        password="postgres",
    )


def _get_openai_client() -> OpenAI:
    # Works with your project-based key
    kwargs = {"api_key": os.environ["OPENAI_API_KEY"]}
    project = os.environ.get("OPENAI_PROJECT_ID")
    if project:
        kwargs["project"] = project
    return OpenAI(**kwargs)


def _embed_query(text: str) -> List[float]:
    client = _get_openai_client()
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return resp.data[0].embedding


def _parse_vector(vec_text: str) -> List[float]:
    """
    Stored as '[0.1,0.2,...]'::vector in Postgres, we turn it into a Python list[float].
    """
    vec_text = vec_text.strip()
    if vec_text.startswith("[") and vec_text.endswith("]"):
        vec_text = vec_text[1:-1]
    if not vec_text:
        return []
    return [float(x) for x in vec_text.split(",") if x.strip()]


def _cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def _infer_desired_styles(query: str) -> List[str]:
    """
    Topic-aware guess of which styles to prefer.
    This is your 'mostly B' logic.
    """
    q = query.lower()

    if any(word in q for word in ["sdr", "outbound", "cold", "pipeline", "follow-up", "follow up"]):
        return ["educational", "playbook", "sales", "story"]

    if any(word in q for word in ["founder", "journey", "origin", "story"]):
        return ["story", "authority", "educational"]

    if any(word in q for word in ["ai meme", "funny", "lol", "joke", "shitpost"]):
        return ["meme", "pattern-interrupt", "educational"]

    if any(word in q for word in ["case study", "results", "roi", "metrics"]):
        return ["authority", "testimonial", "educational"]

    if any(word in q for word in ["launch", "feature", "new release", "update"]):
        return ["sales", "authority", "educational"]

    # Couldn’t guess → signal caller to fall back to default mix
    return []


def _default_style_mix() -> List[str]:
    """
    This is your 'A' fallback: diverse, safe mix.
    """
    return ["educational", "story", "meme", "sales"]


def semantic_search(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Real semantic search:
      - embeds the query
      - pulls all embedded posts from DB
      - scores by cosine similarity
      - tries to mix styles based on topic (C: mostly B, fallback A)
    """
    q_vec = _embed_query(query)

    conn = _get_db_conn()
    cur = conn.cursor()

    # Pull embeddings + captions + style_tags
    cur.execute(
        """
        select
          p.id,
          p.post_id,
          p.caption,
          e.vector::text as vec,
          coalesce(e.style_tags, ARRAY[]::text[]) as style_tags
        from posts_raw p
        join embeddings e on e.post_raw_id = p.id
        """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    posts: List[Dict[str, Any]] = []
    for db_id, post_id, caption, vec_text, style_tags in rows:
        vec = _parse_vector(vec_text)
        if not vec:
            continue
        score = _cosine(q_vec, vec)
        posts.append(
            {
                "db_id": db_id,
                "post_id": post_id,
                "caption": caption,
                "style_tags": list(style_tags or []),
                "score": score,
            }
        )

    # Sort by similarity
    posts.sort(key=lambda p: p["score"], reverse=True)

    if not posts:
        return []

    # Decide style mix: topic-aware first, else default
    desired_styles = _infer_desired_styles(query)
    if not desired_styles:
        desired_styles = _default_style_mix()

    # Deduplicate while keeping order
    seen = set()
    desired_styles = [s for s in desired_styles if not (s in seen or seen.add(s))]

    # Try to pick a diverse set by style
    picked: List[Dict[str, Any]] = []
    used_ids = set()

    # rough share each style gets
    per_style = max(1, limit // max(1, len(desired_styles)))

    for style in desired_styles:
        # all posts that have this style
        style_posts = [p for p in posts if style in p["style_tags"]]
        for p in style_posts[:per_style]:
            if p["post_id"] in used_ids:
                continue
            picked.append(p)
            used_ids.add(p["post_id"])
            if len(picked) >= limit:
                return picked

    # If we still don't have enough, top up with highest scoring posts regardless of style
    for p in posts:
        if len(picked) >= limit:
            break
        if p["post_id"] in used_ids:
            continue
        picked.append(p)
        used_ids.add(p["post_id"])

    return picked