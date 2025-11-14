# app/agents/discovery_agent.py

from typing import List, Dict, Any
import os
import json
import textwrap
from openai import OpenAI


def _get_openai_client() -> OpenAI:
    """
    Build an OpenAI client, honoring OPENAI_API_KEY and optional OPENAI_PROJECT_ID.
    """
    kwargs = {"api_key": os.environ["OPENAI_API_KEY"]}
    project = os.environ.get("OPENAI_PROJECT_ID")
    if project:
        kwargs["project"] = project
    return OpenAI(**kwargs)


def suggest_accounts_for_brand(
    brand_name: str,
    brand_description: str,
    target_audience: str,
    existing_handles: Dict[str, List[str]],
    max_suggestions: int = 15,
) -> List[Dict[str, Any]]:
    """
    Use the LLM to propose social accounts (instagram, facebook, linkedin)
    that our target audience is likely to follow.

    existing_handles = {
      "instagram": ["getfuelai", ...],
      "facebook": ["Fuel AI", ...],
      "linkedin": ["fuelAI", ...]
    }

    Returns a list of dicts:
      {
        "platform": "instagram|facebook|linkedin",
        "handle": "...",
        "display_name": "...",
        "type": "competitor|inspiration|adjacent|meme|viral",
        "reason": "... (why relevant to our audience)",
        "voice_notes": "... (what parts of their tone/format we want to borrow)",
        "fit_score": 0–100 (float)
      }
    """
    client = _get_openai_client()

    system_prompt = textwrap.dedent("""
    You are a research assistant helping a B2B SaaS team find relevant social accounts
    their target audience follows.

    Brand:
    - Product: FuelAI, an AI that runs outbound and follow-ups for sales teams, acting like a human SDR that never gets tired.
    - Target buyers: sales leaders, SDR/BDR managers, RevOps, and founder-led sales teams in B2B SaaS.

    Your job:
    - Propose social media accounts on Instagram, Facebook, and LinkedIn
      that this audience is likely to follow for:
        * outbound and cold outreach
        * SDR/BDR life, memes, and scripts
        * sales frameworks and playbooks
        * pipeline generation and follow-up strategy
    - Include a mix of:
        * direct competitors in AI outbound / automation
        * sales and outbound thought leaders
        * SDR meme / culture accounts
        * viral, high-signal accounts that shape the "sales internet"
        * adjacent sales tools that are VERY outbound-focused (e.g. Outreach, Apollo, SalesLoft)

    STRONG PREFERENCES:
    - PRIORITIZE Instagram and LinkedIn over Facebook.
    - PRIORITIZE:
        * accounts that regularly talk about outbound, SDR work, calling, cold email/DM, sequences, and appointment setting
        * accounts that feel scrappy, operator-led, or creator-led (not just corporate brand accounts)
        * meme/viral accounts that define the humor and language of sales/SDR culture
    - AVOID:
        * generic “growth hacks” accounts without clear sales/outbound focus
        * broad SaaS tools that post generic brand marketing (Slack, Zoom, generic PLG accounts, etc.)
        * celebrity motivation, generic mindset, or non-sales niches

    Output:
    - Return a SINGLE JSON object with a key "accounts" containing a list of objects:
        [
          {
            "platform": "instagram" | "facebook" | "linkedin",
            "handle": "username or page handle",
            "display_name": "Human readable name",
            "type": "competitor" | "inspiration" | "adjacent" | "meme" | "viral",
            "reason": "Why this account is relevant specifically for outbound / SDR / sales leadership.",
            "voice_notes": "What aspects of their tone, pacing, hooks, memes, or content structure FuelAI should borrow or be inspired by.",
            "fit_score": 0–100
          },
          ...
        ]

    Rules:
    - Only include accounts relevant to outbound, SDR/BDR life, sales leadership, sales operations, or RevOps.
    - Explicitly include some SDR meme / viral accounts where appropriate.
    - Do NOT include religion or politics.
    - Do NOT include the brand's own accounts in the suggestions.
    - DO NOT include unrelated SaaS brands or generic productivity tools unless they are clearly sales- or outbound-focused.
    - "fit_score" must be a number between 0 and 100 (100 = perfect ICP fit for FuelAI).
    - Limit to at most 20 suggestions total.
    - Return JSON only (no commentary).
    """)

    user_payload = {
        "brand_name": brand_name,
        "brand_description": brand_description,
        "target_audience": target_audience,
        "existing_handles": existing_handles,
        "max_suggestions": max_suggestions,
    }

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_payload)},
        ],
    )

    content = response.choices[0].message.content

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return []

    accounts = data.get("accounts") or data.get("suggestions") or []

    normalized: List[Dict[str, Any]] = []
    for acc in accounts:
        platform = str(acc.get("platform", "")).lower().strip()
        if platform not in ("instagram", "facebook", "linkedin"):
            continue

        handle = str(acc.get("handle", "")).strip()
        if not handle:
            continue

        # Skip existing handles for that platform
        existing_for_platform = existing_handles.get(platform, [])
        if handle in existing_for_platform:
            continue

        # Fit score as 0–100
        fit_score_raw = acc.get("fit_score", 70)
        try:
            fit_score = float(fit_score_raw)
        except (TypeError, ValueError):
            fit_score = 70.0
        # clamp just in case
        if fit_score < 0:
            fit_score = 0.0
        if fit_score > 100:
            fit_score = 100.0

        acc_type = str(acc.get("type", "inspiration")).lower()
        if acc_type not in ("competitor", "inspiration", "adjacent", "meme", "viral"):
            acc_type = "inspiration"

        # Voice notes about what to copy from their style
        voice_notes = acc.get("voice_notes") or acc.get("voice_reason") or ""

        # Soft filtering:
        # - higher bar for adjacents
        # - meme/viral allowed with slightly different bar
        if acc_type == "adjacent" and fit_score < 75:
            continue
        elif acc_type in ("meme", "viral"):
            if fit_score < 65:
                continue
        else:
            if fit_score < 60:
                continue

        normalized.append(
            {
                "platform": platform,
                "handle": handle,
                "display_name": acc.get("display_name") or handle,
                "type": acc_type,
                "reason": acc.get("reason", ""),
                "voice_notes": voice_notes,
                "fit_score": fit_score,  # 0–100
            }
        )

    # Sort by fit_score descending
    normalized.sort(key=lambda x: x["fit_score"], reverse=True)
    return normalized[:max_suggestions]