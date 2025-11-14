# app/agents/drafting_agent.py

from typing import Dict, Any, List
import os
import json
import textwrap

from openai import OpenAI
from app.agents.semantic_agent import semantic_search


def _get_openai_client() -> OpenAI:
    """
    Reuse the same pattern as semantic_agent: project-based key is supported.
    """
    kwargs = {"api_key": os.environ["OPENAI_API_KEY"]}
    project = os.environ.get("OPENAI_PROJECT_ID")
    if project:
        kwargs["project"] = project
    return OpenAI(**kwargs)


def generate_post_package(topic: str) -> Dict[str, Any]:
    """
    Full post drafting agent.

    - Uses semantic_search() to pull inspiration posts
    - Calls OpenAI to generate:
        * core idea
        * Instagram variant
        * Facebook variant
        * LinkedIn variant
    - Returns a structured dict.
    """

    # 1) Get inspiration posts from semantic search
    inspiration_posts: List[Dict[str, Any]] = semantic_search(topic, limit=5)

    client = _get_openai_client()

    system_prompt = textwrap.dedent("""
    You are the autonomous social media strategist for a B2B SaaS startup called FuelAI.

    Brand:
    - Product: AI that runs outbound and follow-ups for sales teams, acting like a human SDR.
    - Tone: trustworthy, data-driven, friendly, human, conversational, bold, witty, disruptive,
      sarcastic, irreverent (but never mean).
    - CTA style: mentor energy, not pushy. You invite people to think, not pressure them to book now.
    - Banned topics: religion and politics. Never reference them directly or indirectly.

    Goals:
    - Generate *platform-native* post packages for Instagram, Facebook, and LinkedIn.
    - Use inspiration posts ONLY as style and angle references, never plagiarize.
    - Vary post styles over time (educational, story, meme, soft-sales, etc.).
    - Keep everything in plain English, no emojis unless they really serve the message.

    Output:
    You MUST respond with a single JSON object with this shape (no extra text):

    {
      "core_theme": "...",
      "core": {
        "angle": "...",
        "summary": "...",
        "style": "educational | meme | story | sales | authority | etc",
        "reasoning": "why this angle makes sense for FuelAI and this topic"
      },
      "instagram": {
        "hook": "...",
        "caption": "...",
        "hashtags": ["...", "..."],
        "image_prompts": ["prompt 1", "prompt 2"],
        "style": "..."
      },
      "facebook": {
        "hook": "...",
        "caption": "...",
        "hashtags": [],
        "image_prompts": ["..."],
        "style": "..."
      },
      "linkedin": {
        "hook": "...",
        "caption": "...",
        "hashtags": ["...", "..."],
        "image_prompts": ["..."],
        "style": "..."
      }
    }

    Rules:
    - Respect the platform norms:
      * Instagram: tighter copy, punchy, more visual, moderate hashtags.
      * Facebook: relaxed, conversational, fewer or zero hashtags.
      * LinkedIn: thoughtful, structured, slightly more polished.
    - No hard "BOOK A DEMO" sales CTAs. Use soft, mentor-style invitations.
    - Do not mention banned topics (religion, politics).
    - Do NOT include backticks or markdown in your answer. Raw JSON only.
    """)

    # Prepare a compact version of inspiration to avoid overloading the model
    insp_summaries = []
    for p in inspiration_posts:
        insp_summaries.append({
            "post_id": p.get("post_id"),
            "caption": p.get("caption"),
            "style_tags": p.get("style_tags", []),
            "score": p.get("score")
        })

    user_prompt = {
        "topic": topic,
        "inspiration_posts": insp_summaries
    }

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # you can later swap this to a bigger model if you want
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_prompt)},
        ],
    )

    content = response.choices[0].message.content

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # Fallback: return a simple structure if parsing fails
        return {
            "core_theme": topic,
            "core": {
                "angle": "fallback angle",
                "summary": "LLM JSON parsing failed; using fallback.",
                "style": "unknown",
                "reasoning": "Could not parse JSON from model response."
            },
            "instagram": {
                "hook": "fallback IG hook",
                "caption": "fallback IG caption",
                "hashtags": [],
                "image_prompts": [],
                "style": "unknown"
            },
            "facebook": {
                "hook": "fallback FB hook",
                "caption": "fallback FB caption",
                "hashtags": [],
                "image_prompts": [],
                "style": "unknown"
            },
            "linkedin": {
                "hook": "fallback LinkedIn hook",
                "caption": "fallback LinkedIn caption",
                "hashtags": [],
                "image_prompts": [],
                "style": "unknown"
            },
            "debug_raw": content
        }

    # Add the raw inspiration we used, for inspection/debug later if you want
    data["core_theme"] = data.get("core_theme", topic)
    data["inspiration_used"] = insp_summaries
    return data